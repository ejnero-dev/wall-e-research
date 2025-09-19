# 🛡️ GDPR Compliance Guide

**Wall-E Wallapop Automation System - Complete GDPR Implementation**

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏛️ Legal Framework](#-legal-framework)
- [🛠️ Technical Implementation](#-technical-implementation)
- [📊 Database Compliance](#-database-compliance)
- [🔧 Configuration Setup](#-configuration-setup)
- [📱 API Endpoints](#-api-endpoints)
- [✅ Validation & Testing](#-validation--testing)
- [🚨 Incident Response](#-incident-response)

---

## 🎯 Overview

Wall-E Research now includes **comprehensive GDPR compliance** with a **75/100 compliance score**, implementing all required data protection rights and ethical automation practices.

### Key Compliance Features

✅ **Data Minimization**: Only collect necessary data for marketplace automation
✅ **Purpose Limitation**: Data used only for automated sales assistance
✅ **Consent Management**: Full consent collection and withdrawal system
✅ **Right to be Forgotten**: Complete data deletion and anonymization
✅ **Data Portability**: User data export in structured format
✅ **Audit Trails**: Comprehensive logging of all data operations
✅ **Transparency**: Clear automation disclosure to all users
✅ **Human Oversight**: Required human confirmation for critical actions

---

## 🏛️ Legal Framework

### GDPR Articles Implemented

| Article | Description | Implementation |
|---------|-------------|----------------|
| **Art. 5** | Data processing principles | ✅ Data minimization, purpose limitation |
| **Art. 6** | Lawfulness of processing | ✅ Legitimate interest + consent |
| **Art. 7** | Conditions for consent | ✅ Explicit consent collection |
| **Art. 12** | Transparent information | ✅ Automation disclosure required |
| **Art. 15** | Right of access | ✅ Data export functionality |
| **Art. 17** | Right to erasure | ✅ Data deletion and anonymization |
| **Art. 20** | Right to data portability | ✅ Structured data export |
| **Art. 30** | Records of processing | ✅ Comprehensive audit logs |

### Compliance Requirements

**Rate Limiting Compliance:**
- ✅ **5 messages/hour maximum** (ethical automation limit)
- ✅ **3 concurrent conversations maximum**
- ✅ **2 minute minimum delays** between actions
- ✅ **Active hours: 9:00-20:00** (human-like behavior)

**Transparency Requirements:**
- ✅ **Automation disclosure** in first message
- ✅ **Human oversight availability** always mentioned
- ✅ **Opt-out instructions** provided in every interaction
- ✅ **Contact information** for data controller

---

## 🛠️ Technical Implementation

### Database Schema

**New GDPR Tables:**
```sql
consent_records     -- User consent tracking with legal evidence
audit_logs         -- Comprehensive audit trail for all operations
data_retention_schedules -- Automated data deletion scheduling
compliance_reports  -- Compliance monitoring and reporting
```

**Enhanced Buyer Table:**
```sql
-- GDPR Compliance Fields Added
gdpr_consent_given: BOOLEAN
gdpr_consent_date: TIMESTAMP
data_processing_consent: BOOLEAN
marketing_consent: BOOLEAN
anonymized: BOOLEAN
pseudonymized: BOOLEAN
deletion_requested: BOOLEAN
deletion_scheduled_at: TIMESTAMP
data_export_requested: BOOLEAN
```

### Configuration System

**Compliance Mode Activation:**
```python
from src.config_loader import load_config, ConfigMode

# Load GDPR-compliant configuration
config = load_config(ConfigMode.COMPLIANCE)

# Automatic validation of compliance requirements
assert config['wallapop']['behavior']['max_messages_per_hour'] == 5
assert config['security']['gdpr_compliance']['enabled'] == True
```

---

## 📊 Database Compliance

### Consent Management

**Creating Consent Records:**
```python
from src.database.db_manager import DatabaseManager
from src.database.models import ConsentType

db = DatabaseManager(database_url)

# Grant data processing consent
consent_record = await db.grant_consent(
    buyer_id="buyer123",
    consent_type=ConsentType.DATA_PROCESSING,
    evidence={
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "timestamp": "2025-09-19T14:30:00Z",
        "consent_text": "I agree to automated message processing"
    }
)
```

**Checking Consent Status:**
```python
# Verify consent before processing data
has_consent = await db.check_consent(
    buyer_id="buyer123",
    consent_type=ConsentType.DATA_PROCESSING
)

if not has_consent:
    # Stop processing, request consent
    await request_explicit_consent(buyer_id)
```

### Audit Logging

**Comprehensive Audit Trail:**
```python
from src.database.models import AuditAction

# Log all data operations
await db.create_audit_log(
    action=AuditAction.MESSAGE_SENT,
    user_id="buyer123",
    resource_type="conversation",
    resource_id="conv456",
    details={
        "message_content": "[REDACTED]",
        "automated": True,
        "human_approved": False
    },
    ip_address="192.168.1.100",
    user_agent="Wall-E Bot v1.0"
)
```

### Data Rights Implementation

**Right to Access (Article 15):**
```python
# Export all user data in structured format
user_data = await db.export_user_data("buyer123")

# Returns comprehensive data package:
{
    "personal_data": {...},
    "conversations": [...],
    "consents": [...],
    "audit_trail": [...],
    "export_date": "2025-09-19T14:30:00Z"
}
```

**Right to Erasure (Article 17):**
```python
# Schedule data deletion (30-day notice period)
deletion_record = await db.schedule_data_deletion("buyer123")

# Immediate anonymization for sensitive data
await db.anonymize_buyer_data("buyer123")
```

---

## 🔧 Configuration Setup

### Compliance Configuration File

**`config/compliance_overrides.yaml`:**
```yaml
# GDPR Compliance Configuration
app:
  mode: "compliance"
  transparency_notice: "This is an automated assistant"

wallapop:
  behavior:
    max_messages_per_hour: 5          # Ethical limit
    max_concurrent_conversations: 3    # Conservative limit
    human_confirmation_required: true  # MANDATORY
    transparency_disclosure: true      # MANDATORY
    consent_collection: true          # MANDATORY

security:
  gdpr_compliance:
    enabled: true                     # MANDATORY
    data_minimization: true
    purpose_limitation: true
    consent_required: true
    right_to_be_forgotten: true

  data_collection:
    anonymize_data: true              # MANDATORY
    encryption_at_rest: true          # MANDATORY
    personal_data_retention_days: 30   # Minimal retention

anti_detection:
  enabled: false                      # MANDATORY: Disabled for transparency
```

### Environment Variables

**Required for GDPR Compliance:**
```bash
# Database (required for audit trails)
DATABASE_URL=postgresql://user:pass@localhost:5432/wallapop_bot

# Data Protection Officer contact
DPO_EMAIL=dpo@company.com
DPO_PHONE="+34 xxx xxx xxx"

# Legal entity information
COMPANY_NAME="Your Company Name"
COMPANY_ADDRESS="Legal Address"
PRIVACY_POLICY_URL="https://company.com/privacy"
```

### Validation Commands

**Compliance Verification:**
```bash
# Validate GDPR compliance configuration
uv run python scripts/validate_compliance_config.py

# Test compliance endpoints
uv run python -c "
import asyncio
from src.api.dashboard_routes import get_compliance_status, validate_compliance

async def test_compliance():
    status = await get_compliance_status()
    print(f'Compliance Score: {status.compliance_score}/100')
    validation = await validate_compliance()
    print(f'Status: {validation[\"status\"]}')

asyncio.run(test_compliance())
"
```

---

## 📱 API Endpoints

### Compliance Monitoring

**GET /api/dashboard/compliance/status**
```json
{
  "gdpr_enabled": true,
  "audit_logging_active": true,
  "rate_limit_compliant": true,
  "human_oversight_enabled": true,
  "transparency_mode": true,
  "consent_system_active": true,
  "current_rate_limit": 5,
  "max_allowed_rate": 5,
  "compliance_score": 75.0,
  "last_audit_check": "2025-09-19T14:30:00Z"
}
```

**POST /api/dashboard/compliance/validate**
```json
{
  "status": "compliant",
  "checks": {
    "rate_limit": "PASS",
    "gdpr": "PASS",
    "human_oversight": "PASS",
    "transparency": "PASS"
  },
  "recommendations": [],
  "timestamp": "2025-09-19T14:30:00Z"
}
```

### Consent Management

**POST /api/dashboard/compliance/consents**
```bash
curl -X POST "http://localhost:8000/api/dashboard/compliance/consents" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_id": "buyer123",
    "consent_type": "data_processing",
    "evidence": {
      "ip_address": "192.168.1.1",
      "timestamp": "2025-09-19T14:30:00Z"
    }
  }'
```

**DELETE /api/dashboard/compliance/consents/{buyer_id}**
```bash
# Withdraw consent (Right to object)
curl -X DELETE "http://localhost:8000/api/dashboard/compliance/consents/buyer123" \
  -H "Content-Type: application/json" \
  -d '{"consent_type": "data_processing"}'
```

### Data Rights

**POST /api/dashboard/compliance/data-export/{buyer_id}**
```bash
# Export user data (Right to data portability)
curl -X POST "http://localhost:8000/api/dashboard/compliance/data-export/buyer123"
```

**DELETE /api/dashboard/compliance/user-data/{buyer_id}**
```bash
# Schedule data deletion (Right to erasure)
curl -X DELETE "http://localhost:8000/api/dashboard/compliance/user-data/buyer123"
```

---

## ✅ Validation & Testing

### Automated Compliance Testing

**Pre-deployment Checklist:**
```bash
# 1. Validate configuration compliance
uv run python scripts/validate_compliance_config.py
# Expected: ✅ Compliance configuration validation PASSED

# 2. Test database compliance models
uv run python -c "
from src.database.db_manager import DatabaseManager
db = DatabaseManager('postgresql://user:pass@localhost:5432/wallapop_bot')
print('✅ Database compliance models ready')
"

# 3. Verify API endpoints
uv run python -c "
import asyncio
from src.api.dashboard_routes import get_compliance_status
async def test():
    status = await get_compliance_status()
    assert status.compliance_score >= 75, 'Compliance score too low'
    print('✅ API compliance endpoints working')
asyncio.run(test())
"

# 4. Check rate limiting
grep -q "max_messages_per_hour: 5" config/compliance_overrides.yaml && \
echo "✅ Rate limits correctly configured" || \
echo "❌ Rate limits not compliant"
```

### Manual Verification

**Legal Compliance Checklist:**
- [ ] **GDPR lawful basis** documented and valid
- [ ] **Data Processing Agreement** signed with any processors
- [ ] **Privacy Policy** updated with automation disclosure
- [ ] **Consent collection** mechanism deployed and tested
- [ ] **Data retention policies** implemented and scheduled
- [ ] **Data Protection Officer** contact information configured
- [ ] **Breach notification** procedures established
- [ ] **Cross-border transfer** safeguards (if applicable)

---

## 🚨 Incident Response

### Data Breach Response

**Immediate Actions (0-1 hour):**
1. **Stop all automated processing** immediately
2. **Assess scope** of potential data exposure
3. **Secure** affected systems and data
4. **Document** incident timeline and impact

**Legal Obligations (1-72 hours):**
```bash
# Generate incident report
uv run python scripts/generate_incident_report.py \
  --incident-id "INC-2025-001" \
  --severity "high" \
  --affected-users "buyer123,buyer456"

# Export audit logs for investigation
curl -X GET "http://localhost:8000/api/dashboard/compliance/audit-logs?limit=1000"
```

**Notification Requirements:**
- **Supervisory Authority**: Within 72 hours if high risk
- **Data Subjects**: Without undue delay if high risk to rights
- **DPO/Legal Team**: Immediately
- **Senior Management**: Within 1 hour

### Compliance Violations

**Common Violation Responses:**
```bash
# Immediate rate limit reduction
curl -X POST "http://localhost:8000/api/dashboard/config/update" \
  -d '{"key": "max_messages_per_hour", "value": 1, "apply_immediately": true}'

# Emergency stop all automation
curl -X POST "http://localhost:8000/api/dashboard/auto-detection/stop"

# Generate compliance report
uv run python scripts/generate_compliance_report.py \
  --period "last-30-days" \
  --include-recommendations
```

---

## 📞 Support & Resources

### Technical Support
- **Configuration Issues**: Check [Configuration Guide](../getting-started/CONFIGURATION_GUIDE.md)
- **Database Problems**: Review [Database Architecture](../development/ARCHITECTURE_OVERVIEW.md)
- **API Questions**: Consult [API Reference](../development/API_REFERENCE.md)

### Legal Resources
- **GDPR Official Text**: [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- **Spanish DPA (AEPD)**: [agpd.es](https://www.aepd.es/)
- **Privacy Policy Generator**: [gdpr.eu](https://gdpr.eu/privacy-notice/)

### Emergency Contacts
- **Data Protection Officer**: dpo@company.com
- **Legal Team**: legal@company.com
- **Technical Support**: support@company.com

---

**⚖️ Remember**: This guide provides technical implementation details. Always consult with qualified legal counsel for compliance verification and legal advice specific to your jurisdiction and use case.

**📅 Document Version**: 1.0 | **Last Updated**: September 19, 2025 | **Next Review**: December 19, 2025