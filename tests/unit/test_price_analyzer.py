#!/usr/bin/env python3
"""
Unit tests for Price Analyzer module
Tests market price analysis, competitive intelligence, and pricing strategies
"""

import pytest

# Mark all tests in this file as unit tests for price analyzer
pytestmark = [pytest.mark.unit, pytest.mark.price_analyzer, pytest.mark.fast]
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from price_analyzer.analyzer import (
    PriceAnalyzer,
    PriceData,
    PriceAnalysis,
    MarketData,
    AnalysisStrategy,
    ProductCondition,
)


class TestPriceAnalyzer:
    """Test suite for PriceAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create PriceAnalyzer instance for testing"""
        return PriceAnalyzer()

    @pytest.fixture
    def sample_price_data(self):
        """Sample price data for testing"""
        return [
            PriceData(
                platform="wallapop",
                price=450.0,
                condition="como nuevo",
                location="Madrid",
                seller_rating=4.8,
                posted_days_ago=2,
            ),
            PriceData(
                platform="wallapop",
                price=380.0,
                condition="usado",
                location="Barcelona",
                seller_rating=4.2,
                posted_days_ago=5,
            ),
            PriceData(
                platform="amazon",
                price=520.0,
                condition="nuevo",
                location="España",
                seller_rating=4.9,
                posted_days_ago=0,
            ),
            PriceData(
                platform="ebay",
                price=395.0,
                condition="usado",
                location="Madrid",
                seller_rating=4.1,
                posted_days_ago=3,
            ),
        ]

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert hasattr(analyzer, "analyze_market_price")
        assert hasattr(analyzer, "suggest_price")

    def test_price_data_validation(self):
        """Test PriceData validation and creation"""
        price_data = PriceData(
            platform="wallapop", price=450.0, condition="como nuevo", location="Madrid"
        )
        assert price_data.platform == "wallapop"
        assert price_data.price == 450.0
        assert price_data.condition == "como nuevo"
        assert price_data.location == "Madrid"

    def test_market_analysis_basic(self, analyzer, sample_price_data):
        """Test basic market analysis functionality"""
        product_name = "iPhone 12 128GB"
        current_price = 450.0
        condition = ProductCondition.COMO_NUEVO

        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name=product_name,
                current_price=current_price,
                condition=condition,
            )

            assert isinstance(analysis, PriceAnalysis)
            assert analysis.product_name == product_name
            assert analysis.current_price == current_price
            assert analysis.market_data is not None
            assert len(analysis.market_data.price_points) == len(sample_price_data)

    def test_price_statistics_calculation(self, analyzer, sample_price_data):
        """Test price statistics calculation"""
        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
            )

            stats = analysis.market_data.statistics
            assert stats["min_price"] == 380.0
            assert stats["max_price"] == 520.0
            assert "avg_price" in stats
            assert "median_price" in stats
            assert "std_deviation" in stats

    def test_competitive_positioning(self, analyzer, sample_price_data):
        """Test competitive positioning analysis"""
        current_price = 450.0

        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=current_price,
                condition=ProductCondition.COMO_NUEVO,
            )

            positioning = analysis.competitive_positioning
            assert positioning["percentile"] is not None
            assert 0 <= positioning["percentile"] <= 100
            assert "above_market" in positioning
            assert "below_market" in positioning

    def test_price_suggestions(self, analyzer, sample_price_data):
        """Test price suggestion generation"""
        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
                strategy=AnalysisStrategy.BALANCED,
            )

            suggestions = analysis.price_suggestions
            assert "quick_sale" in suggestions
            assert "market_competitive" in suggestions
            assert "maximum_profit" in suggestions

            # Validate price ranges
            assert suggestions["quick_sale"] <= suggestions["market_competitive"]
            assert suggestions["market_competitive"] <= suggestions["maximum_profit"]

    def test_condition_adjustment(self, analyzer):
        """Test price adjustment based on product condition"""
        base_price = 500.0

        # Test different conditions
        conditions_and_multipliers = [
            (ProductCondition.NUEVO, 1.0),
            (ProductCondition.COMO_NUEVO, 0.85),
            (ProductCondition.BUEN_ESTADO, 0.70),
            (ProductCondition.USADO, 0.55),
        ]

        for condition, expected_multiplier in conditions_and_multipliers:
            adjusted_price = analyzer._adjust_price_for_condition(base_price, condition)
            expected_price = base_price * expected_multiplier
            assert abs(adjusted_price - expected_price) < 0.01

    def test_location_adjustment(self, analyzer):
        """Test price adjustment based on location"""
        base_price = 500.0

        # Test major cities (typically higher prices)
        madrid_price = analyzer._adjust_price_for_location(base_price, "Madrid")
        barcelona_price = analyzer._adjust_price_for_location(base_price, "Barcelona")

        assert madrid_price >= base_price * 0.95  # At least 95% of base price
        assert barcelona_price >= base_price * 0.95

        # Test smaller cities (typically lower prices)
        small_city_price = analyzer._adjust_price_for_location(base_price, "Cuenca")
        assert small_city_price <= base_price * 1.05  # At most 105% of base price

    def test_confidence_scoring(self, analyzer, sample_price_data):
        """Test confidence score calculation"""
        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
            )

            confidence = analysis.confidence_score
            assert 0 <= confidence <= 1

            # More data points should increase confidence
            assert (
                confidence > 0.5
            )  # With 4 data points, confidence should be reasonable

    def test_trend_analysis(self, analyzer):
        """Test market trend analysis"""
        # Mock historical data showing price decline
        historical_data = [
            {"date": "2024-01-01", "avg_price": 550.0},
            {"date": "2024-01-15", "avg_price": 520.0},
            {"date": "2024-02-01", "avg_price": 480.0},
            {"date": "2024-02-15", "avg_price": 450.0},
        ]

        with patch.object(
            analyzer, "_get_historical_prices", return_value=historical_data
        ):
            trend = analyzer._analyze_price_trend("iPhone 12 128GB")

            assert "direction" in trend
            assert trend["direction"] in ["rising", "falling", "stable"]
            assert "change_percentage" in trend
            assert "velocity" in trend

    def test_fraud_detection_integration(self, analyzer, sample_price_data):
        """Test integration with fraud detection"""
        # Add suspicious price data
        suspicious_data = sample_price_data + [
            PriceData(
                platform="wallapop",
                price=200.0,  # Suspiciously low price
                condition="nuevo",
                location="Madrid",
                seller_rating=0.0,  # New seller
                posted_days_ago=0,
            )
        ]

        with patch.object(
            analyzer, "_collect_market_data", return_value=suspicious_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
            )

            # Should detect suspicious pricing
            risk_factors = analysis.risk_assessment
            assert "suspicious_low_prices" in risk_factors
            assert risk_factors["overall_risk_score"] > 0

    @pytest.mark.parametrize(
        "strategy",
        [
            AnalysisStrategy.QUICK_SALE,
            AnalysisStrategy.BALANCED,
            AnalysisStrategy.MAXIMUM_PROFIT,
        ],
    )
    def test_different_strategies(self, analyzer, sample_price_data, strategy):
        """Test different pricing strategies"""
        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
                strategy=strategy,
            )

            assert analysis.strategy == strategy
            suggestions = analysis.price_suggestions

            if strategy == AnalysisStrategy.QUICK_SALE:
                # Quick sale should suggest lower prices
                assert (
                    suggestions["recommended"]
                    <= analysis.market_data.statistics["avg_price"]
                )
            elif strategy == AnalysisStrategy.MAXIMUM_PROFIT:
                # Maximum profit should suggest higher prices
                assert (
                    suggestions["recommended"]
                    >= analysis.market_data.statistics["avg_price"]
                )

    def test_insufficient_data_handling(self, analyzer):
        """Test handling of insufficient market data"""
        with patch.object(analyzer, "_collect_market_data", return_value=[]):
            analysis = analyzer.analyze_market_price(
                product_name="Rare Product XYZ",
                current_price=100.0,
                condition=ProductCondition.USADO,
            )

            assert analysis.confidence_score < 0.3  # Low confidence
            assert "insufficient_data" in analysis.warnings
            # Should still provide fallback suggestions
            assert analysis.price_suggestions is not None

    def test_currency_handling(self, analyzer):
        """Test proper currency handling"""
        price_data = [
            PriceData(
                platform="test", price=450.0, condition="usado", location="Madrid"
            )
        ]

        with patch.object(analyzer, "_collect_market_data", return_value=price_data):
            analysis = analyzer.analyze_market_price(
                product_name="Test Product",
                current_price=450.0,
                condition=ProductCondition.USADO,
                currency="EUR",
            )

            assert analysis.currency == "EUR"
            # All prices should be in the same currency
            for suggestion in analysis.price_suggestions.values():
                assert isinstance(suggestion, (int, float, Decimal))

    def test_platform_weighting(self, analyzer, sample_price_data):
        """Test platform-specific weighting in analysis"""
        with patch.object(
            analyzer, "_collect_market_data", return_value=sample_price_data
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12 128GB",
                current_price=450.0,
                condition=ProductCondition.COMO_NUEVO,
            )

            # Wallapop prices should have higher weight for Wallapop listing
            platform_weights = analysis.market_data.platform_weights
            assert platform_weights.get("wallapop", 0) >= platform_weights.get(
                "ebay", 0
            )

    def test_seasonal_adjustments(self, analyzer):
        """Test seasonal price adjustments"""
        import datetime

        # Mock current date to test seasonal adjustments
        with patch("datetime.datetime") as mock_date:
            # Christmas season - electronics typically more expensive
            mock_date.now.return_value = datetime.datetime(2024, 12, 15)

            seasonal_factor = analyzer._get_seasonal_factor("iPhone 12", "electronics")
            assert seasonal_factor >= 1.0  # Should increase price during holidays

    def test_error_handling(self, analyzer):
        """Test error handling in price analysis"""
        # Test with invalid inputs
        with pytest.raises(ValueError):
            analyzer.analyze_market_price(
                product_name="",  # Empty product name
                current_price=-100.0,  # Negative price
                condition=ProductCondition.USADO,
            )

        # Test with network errors
        with patch.object(
            analyzer, "_collect_market_data", side_effect=Exception("Network error")
        ):
            analysis = analyzer.analyze_market_price(
                product_name="iPhone 12",
                current_price=450.0,
                condition=ProductCondition.USADO,
            )

            # Should handle gracefully and provide fallback
            assert analysis is not None
            assert "error" in analysis.warnings


class TestPriceData:
    """Test suite for PriceData class"""

    def test_price_data_creation(self):
        """Test PriceData creation and validation"""
        data = PriceData(
            platform="wallapop", price=450.0, condition="usado", location="Madrid"
        )

        assert data.platform == "wallapop"
        assert data.price == 450.0
        assert data.condition == "usado"
        assert data.location == "Madrid"

    def test_price_data_comparison(self):
        """Test PriceData comparison methods"""
        data1 = PriceData(
            platform="wallapop", price=450.0, condition="usado", location="Madrid"
        )
        data2 = PriceData(
            platform="wallapop", price=380.0, condition="usado", location="Barcelona"
        )

        assert data1 > data2  # Higher price
        assert data2 < data1  # Lower price

    def test_price_data_serialization(self):
        """Test PriceData serialization for API responses"""
        data = PriceData(
            platform="wallapop",
            price=450.0,
            condition="usado",
            location="Madrid",
            seller_rating=4.5,
            posted_days_ago=3,
        )

        serialized = data.to_dict()
        assert isinstance(serialized, dict)
        assert serialized["platform"] == "wallapop"
        assert serialized["price"] == 450.0


class TestMarketData:
    """Test suite for MarketData class"""

    def test_market_data_aggregation(self):
        """Test market data aggregation and statistics"""
        price_points = [
            PriceData("wallapop", 450.0, "usado", "Madrid"),
            PriceData("wallapop", 380.0, "usado", "Barcelona"),
            PriceData("ebay", 420.0, "usado", "España"),
        ]

        market_data = MarketData(price_points)
        stats = market_data.calculate_statistics()

        assert stats["count"] == 3
        assert stats["min_price"] == 380.0
        assert stats["max_price"] == 450.0
        assert 400.0 <= stats["avg_price"] <= 425.0  # Approximate average

    def test_platform_distribution(self):
        """Test platform distribution analysis"""
        price_points = [
            PriceData("wallapop", 450.0, "usado", "Madrid"),
            PriceData("wallapop", 380.0, "usado", "Barcelona"),
            PriceData("ebay", 420.0, "usado", "España"),
            PriceData("amazon", 500.0, "nuevo", "España"),
        ]

        market_data = MarketData(price_points)
        distribution = market_data.get_platform_distribution()

        assert distribution["wallapop"] == 2
        assert distribution["ebay"] == 1
        assert distribution["amazon"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
