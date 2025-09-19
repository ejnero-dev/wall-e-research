# 🏛️ Legal Deployment Guide

**Production Deployment with Full GDPR Compliance**

## 🎯 Pre-Deployment Requirements

### Legal Prerequisites
- [ ] **Legal counsel consultation** completed
- [ ] **Data Processing Agreement** signed
- [ ] **Privacy Policy** updated with automation disclosure
- [ ] **Data Protection Officer** appointed (if required)
- [ ] **Lawful basis** for processing documented

### Technical Prerequisites
```bash
# Verify compliance configuration
uv run python scripts/validate_compliance_config.py

# Expected compliance score ≥ 75/100
# Expected rate limit = 5 messages/hour
# Expected GDPR features: enabled
```

## 🚀 Production Deployment

### 1. Environment Configuration
```bash
# Set production environment variables
export DATABASE_URL="postgresql://user:pass@prod-db:5432/wallapop_bot"
export DPO_EMAIL="dpo@company.com"
export COMPANY_NAME="Your Legal Entity Name"
export PRIVACY_POLICY_URL="https://company.com/privacy"

# Load compliance configuration
export CONFIG_MODE="compliance"
```

### 2. Database Migration
```bash
# Apply GDPR compliance migrations
uv run alembic upgrade head

# Verify compliance tables exist
psql $DATABASE_URL -c "\dt" | grep -E "(consent_records|audit_logs|compliance_reports)"
```

### 3. Start Services
```bash
# Start with compliance mode enabled
CONFIG_MODE=compliance uv run python -m uvicorn src.api.dashboard_server:app --host 0.0.0.0 --port 8000

# Verify compliance status
curl -s http://localhost:8000/api/dashboard/compliance/status | jq .compliance_score
# Must return: 75.0 or higher
```

## ⚖️ Legal Compliance Monitoring

### Daily Monitoring
```bash
# Check compliance status daily
curl -s http://localhost:8000/api/dashboard/compliance/status

# Monitor rate limits
curl -s http://localhost:8000/api/dashboard/metrics/summary | jq .msg_rate
# Must be ≤ 5 messages/hour
```

### Weekly Reports
```bash
# Generate weekly compliance report
curl -s http://localhost:8000/api/dashboard/compliance/reports

# Export audit logs for review
curl -s "http://localhost:8000/api/dashboard/compliance/audit-logs?limit=1000"
```

## 🚨 Emergency Procedures

### Immediate Stop
```bash
# Emergency shutdown of all automation
curl -X POST http://localhost:8000/api/dashboard/auto-detection/stop

# Reduce rate limit to minimum
curl -X POST http://localhost:8000/api/dashboard/config/update \
  -d '{"key": "max_messages_per_hour", "value": 1}'
```

### Data Subject Requests
```bash
# Data export (Right to portability)
curl -X POST "http://localhost:8000/api/dashboard/compliance/data-export/{buyer_id}"

# Data deletion (Right to erasure)
curl -X DELETE "http://localhost:8000/api/dashboard/compliance/user-data/{buyer_id}"
```

## 📞 Legal Contacts

- **Data Protection Officer**: dpo@company.com
- **Legal Team**: legal@company.com
- **Emergency Contact**: +34 xxx xxx xxx

---

**⚠️ IMPORTANT**: This system implements technical compliance measures. Legal compliance requires ongoing monitoring, legal counsel, and regular audits. Always consult qualified legal professionals for regulatory compliance in your jurisdiction.