# 🛡️ LÍMITES ÉTICOS DE USO - Bot de Wallapop

## ⚠️ ADVERTENCIA CRÍTICA

Este sistema presenta **RIESGOS LEGALES SIGNIFICATIVOS** y NO debe usarse en producción sin implementar las medidas de compliance requeridas.

## 🚫 PROHIBIDO ABSOLUTAMENTE

### Uso Comercial Sin Compliance:
- ❌ **Operación sin consentimiento explícito** de compradores
- ❌ **Elusión de medidas anti-bot** de Wallapop
- ❌ **Envío masivo** de mensajes (>5 conversaciones/día)
- ❌ **Automatización completa** sin supervisión humana
- ❌ **Uso 24/7** sin pausas humanizadas
- ❌ **Ocultación de naturaleza automatizada**

### Violaciones de Privacidad:
- ❌ **Recolección de datos** sin consentimiento RGPD
- ❌ **Almacenamiento inseguro** de información personal
- ❌ **Uso de datos** para fines no consentidos
- ❌ **Falta de mecanismo de eliminación** de datos

## ✅ USO ÉTICO PERMITIDO (Con Implementaciones)

### Modo "Asistente Transparente":
- ✅ **Identificación clara** como asistente automatizado
- ✅ **Consentimiento explícito** antes de continuar conversaciones
- ✅ **Supervisión humana** para todas las decisiones críticas
- ✅ **Rate limiting conservador** (máx 5 acciones/hora)
- ✅ **Respuesta inmediata** a solicitudes de stop

### Funcionalidades Éticas:
- ✅ **Notificaciones de mensajes** nuevos (solo alertas)
- ✅ **Sugerencias de respuesta** (con confirmación humana)
- ✅ **Organización de conversaciones** existentes
- ✅ **Análisis de sentimiento** para priorización

## 📋 REQUERIMIENTOS OBLIGATORIOS

### Antes de Cualquier Uso:
1. **Consulta legal especializada** obligatoria
2. **Implementación de consentimiento** explícito
3. **Reducción de rate limits** a niveles humanos
4. **Eliminación de anti-detección** agresivo
5. **Sistema seguro** de credenciales

### Durante Operación:
1. **Máximo 3 conversaciones** simultáneas
2. **Pausas mínimas 2 minutos** entre acciones
3. **Identificación como bot** en primer mensaje
4. **Logging sin datos** personales
5. **Monitoreo continuo** de compliance

## 🎯 CONFIGURACIÓN ÉTICA RECOMENDADA

### Rate Limits Seguros:
```yaml
# config.yaml - Configuración ética
scraper:
  max_messages_per_hour: 5        # Reducido de 50
  max_actions_per_minute: 0.5     # 1 acción cada 2 minutos
  min_delay_seconds: 120          # Mínimo 2 minutos
  max_concurrent_conversations: 3  # Máximo 3 chats
  require_human_approval: true     # Confirmación humana
```

### Mensaje Inicial Obligatorio:
```
"Hola! Soy [TU NOMBRE] y uso un asistente automatizado para gestionar mis ventas. 
¿Está bien si continuamos? Puedes pedirme que pare en cualquier momento y 
eliminaré todos tus datos. ¿Te parece bien continuar?"
```

## 🔍 INDICADORES DE RIESGO

### Detener Operación Si:
- Tasa de respuesta >90% (muy sospechoso)
- Tiempo de respuesta <60 segundos consistente
- Más de 10 mensajes enviados/día
- Patrones exactos de respuesta repetidos
- Quejas de usuarios sobre spam

### Alertas Automáticas:
- Monitor de cambios en ToS de Wallapop
- Detección de patrones bot
- Tasa de bloqueos por usuarios >5%
- Tiempo de actividad >8 horas/día

## 📞 CONTACTOS DE EMERGENCIA

### En Caso de Problemas Legales:
1. **Suspender operación** inmediatamente
2. **Documentar** todas las conversaciones
3. **Contactar abogado** especializado
4. **Notificar** a usuarios afectados
5. **Eliminar datos** si es requerido

## 🏛️ MARCO LEGAL APLICABLE

### Normativas Relevantes:
- **RGPD (Reglamento General de Protección de Datos)**
- **LOPD-GDD (Ley Orgánica de Protección de Datos)**
- **Términos de Servicio de Wallapop**
- **Directiva de Comercio Electrónico**
- **Código de Conducta de Marketing Digital**

## 📝 REGISTRO DE COMPLIANCE

### Documentación Obligatoria:
- [ ] Revisión legal completada
- [ ] Consentimientos obtenidos y archivados
- [ ] Rate limits configurados correctamente
- [ ] Sistema de opt-out implementado
- [ ] Monitoreo de compliance activo
- [ ] Backup seguro de configuraciones

## 🚨 DESCARGO DE RESPONSABILIDAD

**EL USO DE ESTE SISTEMA ES RESPONSABILIDAD EXCLUSIVA DEL USUARIO.**

Los desarrolladores NO se hacen responsables de:
- Violaciones de términos de servicio
- Multas o sanciones legales
- Bloqueos o suspensiones de cuentas
- Daños reputacionales o comerciales
- Problemas de privacidad o RGPD

**USAR BAJO TU PROPIO RIESGO Y RESPONSABILIDAD LEGAL.**

---

*Documento actualizado: 1 de agosto de 2025*
*Próxima revisión obligatoria: 1 de septiembre de 2025*