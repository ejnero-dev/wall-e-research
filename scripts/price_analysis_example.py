#!/usr/bin/env python3
"""
Ejemplo de uso del Sistema de Análisis de Precios
Demuestra cómo analizar precios para diferentes productos
"""

import asyncio
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import box

# Importar el analizador (ajustar path según tu estructura)
import sys

sys.path.append("../src")
from price_analyzer.analyzer import PriceAnalyzer

console = Console()


async def analyze_single_product():
    """Ejemplo: Analizar un producto individual"""
    console.print("\n[bold blue]📊 Análisis de Precio Individual[/bold blue]\n")

    analyzer = PriceAnalyzer()

    # Producto a analizar
    product = "iPhone 12 128GB"
    condition = "buen estado"

    with Progress() as progress:
        task = progress.add_task(f"[cyan]Analizando {product}...", total=100)

        # Simular progreso (en producción sería real)
        progress.update(task, advance=30, description="[cyan]Buscando en Wallapop...")
        await asyncio.sleep(1)

        progress.update(task, advance=30, description="[cyan]Buscando en Amazon...")
        await asyncio.sleep(1)

        progress.update(task, advance=40, description="[cyan]Analizando datos...")
        await asyncio.sleep(1)

    # Simular resultados (en producción vendría del análisis real)
    analysis = {
        "avg_price": 485.50,
        "median_price": 475.00,
        "min_price": 380.00,
        "max_price": 650.00,
        "suggested_price": 450.00,
        "competitive_price": 425.00,
        "premium_price": 525.00,
        "total_listings": 47,
        "active_listings": 42,
        "confidence_score": 88.5,
        "market_trend": "bajando",
    }

    # Mostrar resultados en tabla
    table = Table(title=f"Análisis de Precio: {product}", box=box.ROUNDED)

    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")
    table.add_column("Recomendación", style="green")

    table.add_row(
        "Precio Promedio", f"{analysis['avg_price']:.2f}€", "Referencia del mercado"
    )
    table.add_row(
        "Precio Mediano", f"{analysis['median_price']:.2f}€", "Más estable que promedio"
    )
    table.add_row(
        "Rango de Precios",
        f"{analysis['min_price']:.2f}€ - {analysis['max_price']:.2f}€",
        "Variación del mercado",
    )
    table.add_section()
    table.add_row(
        "[bold]Precio Sugerido[/bold]",
        f"[bold]{analysis['suggested_price']:.2f}€[/bold]",
        "[bold]RECOMENDADO[/bold]",
    )
    table.add_row(
        "Precio Competitivo",
        f"{analysis['competitive_price']:.2f}€",
        "Venta en 1-3 días",
    )
    table.add_row(
        "Precio Premium", f"{analysis['premium_price']:.2f}€", "Maximizar beneficio"
    )
    table.add_section()
    table.add_row(
        "Anuncios Analizados",
        str(analysis["total_listings"]),
        f"{analysis['active_listings']} activos",
    )
    table.add_row(
        "Confianza", f"{analysis['confidence_score']:.1f}%", "Alta confianza ✓"
    )
    table.add_row("Tendencia", analysis["market_trend"], "⬇️ Considera bajar precio")

    console.print(table)


async def compare_multiple_products():
    """Ejemplo: Comparar precios de varios productos"""
    console.print("\n[bold blue]📊 Comparación de Múltiples Productos[/bold blue]\n")

    products = [
        {"name": "iPhone 12 128GB", "condition": "como nuevo"},
        {"name": "iPhone 11 128GB", "condition": "buen estado"},
        {"name": "iPhone 13 128GB", "condition": "como nuevo"},
    ]

    # Tabla comparativa
    table = Table(title="Comparación de Precios iPhone", box=box.ROUNDED)

    table.add_column("Modelo", style="cyan", no_wrap=True)
    table.add_column("Condición", style="yellow")
    table.add_column("P. Sugerido", style="green", justify="right")
    table.add_column("P. Competitivo", style="blue", justify="right")
    table.add_column("P. Premium", style="magenta", justify="right")
    table.add_column("Tendencia", style="white")

    # Datos simulados
    results = [
        {"suggested": 450, "competitive": 425, "premium": 525, "trend": "↓"},
        {"suggested": 350, "competitive": 325, "premium": 400, "trend": "→"},
        {"suggested": 650, "competitive": 625, "premium": 725, "trend": "↑"},
    ]

    for product, result in zip(products, results):
        table.add_row(
            product["name"],
            product["condition"],
            f"{result['suggested']}€",
            f"{result['competitive']}€",
            f"{result['premium']}€",
            result["trend"],
        )

    console.print(table)


async def price_strategy_simulator():
    """Ejemplo: Simulador de estrategias de precio"""
    console.print("\n[bold blue]🎯 Simulador de Estrategias de Precio[/bold blue]\n")

    base_price = 450.00

    table = Table(title="Estrategias de Precio para iPhone 12", box=box.ROUNDED)

    table.add_column("Estrategia", style="cyan", no_wrap=True)
    table.add_column("Precio", style="magenta", justify="right")
    table.add_column("Tiempo Estimado", style="yellow")
    table.add_column("Probabilidad Venta", style="green")
    table.add_column("Recomendado Para", style="white")

    strategies = [
        {
            "name": "🚀 Venta Flash",
            "price": base_price * 0.90,
            "time": "1-2 días",
            "probability": "95%",
            "for": "Necesitas dinero rápido",
        },
        {
            "name": "⚡ Competitivo",
            "price": base_price * 0.95,
            "time": "3-5 días",
            "probability": "85%",
            "for": "Venta rápida sin prisa",
        },
        {
            "name": "⚖️ Equilibrado",
            "price": base_price,
            "time": "1 semana",
            "probability": "70%",
            "for": "Mejor relación precio/tiempo",
        },
        {
            "name": "💎 Premium",
            "price": base_price * 1.10,
            "time": "2-3 semanas",
            "probability": "40%",
            "for": "Sin prisa, máximo beneficio",
        },
        {
            "name": "👑 Coleccionista",
            "price": base_price * 1.20,
            "time": "1+ mes",
            "probability": "15%",
            "for": "Producto único/especial",
        },
    ]

    for strategy in strategies:
        table.add_row(
            strategy["name"],
            f"{strategy['price']:.2f}€",
            strategy["time"],
            strategy["probability"],
            strategy["for"],
        )

    console.print(table)

    # Recomendación
    console.print("\n[bold green]💡 Recomendación:[/bold green]")
    console.print(
        "Para la mayoría de vendedores, la estrategia [bold]Equilibrada[/bold] ofrece"
    )
    console.print("el mejor balance entre tiempo de venta y beneficio obtenido.\n")


async def market_insights():
    """Ejemplo: Insights del mercado"""
    console.print("\n[bold blue]📈 Insights del Mercado[/bold blue]\n")

    # Datos simulados de distribución de precios
    distribution = {
        "0-300€": 5,
        "300-400€": 15,
        "400-500€": 45,
        "500-600€": 25,
        "600€+": 10,
    }

    console.print("[bold]Distribución de Precios - iPhone 12[/bold]")

    for range_price, percentage in distribution.items():
        bar = "█" * (percentage // 5)
        console.print(f"{range_price:>10} | {bar} {percentage}%")

    console.print("\n[bold]🔍 Insights Clave:[/bold]")
    console.print("• El 45% de los anuncios están entre 400-500€ (zona óptima)")
    console.print("• Solo el 5% están por debajo de 300€ (posibles gangas o problemas)")
    console.print("• El 10% por encima de 600€ tienen pocas ventas")
    console.print("• Precio sweet spot: 425-475€ para venta en <1 semana")


async def main():
    """Función principal que ejecuta todos los ejemplos"""
    console.print(
        "[bold magenta]🤖 Sistema de Análisis de Precios - Ejemplos[/bold magenta]"
    )
    console.print("=" * 60)

    # Ejecutar ejemplos
    await analyze_single_product()
    await asyncio.sleep(1)

    await compare_multiple_products()
    await asyncio.sleep(1)

    await price_strategy_simulator()
    await asyncio.sleep(1)

    await market_insights()

    # Guardar análisis
    console.print("\n[bold blue]💾 Guardando análisis...[/bold blue]")

    analysis_data = {
        "timestamp": datetime.now().isoformat(),
        "product": "iPhone 12 128GB",
        "suggested_price": 450.00,
        "confidence": 88.5,
        "market_trend": "bajando",
    }

    with open("../data/price_analysis_example.json", "w") as f:
        json.dump(analysis_data, f, indent=2)

    console.print(
        "[green]✅ Análisis guardado en data/price_analysis_example.json[/green]"
    )
    console.print("\n[bold green]¡Análisis completado con éxito![/bold green] 🎉")


if __name__ == "__main__":
    asyncio.run(main())
