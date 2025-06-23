DynamoDB Tables:

1. `Regressivos` Table:
   - Primary Key: `regressivoId` (String, UUID)
   - Attributes:
     - `release` (String)
     - `ambiente` (String, e.g., "Homolog", "Alpha")
     - `statusGeral` (String, e.g., "ativo", "finalizado")
     - `slaInicio` (String, ISO 8601 datetime)
     - `slaFim` (String, ISO 8601 datetime)
     - `liberadoEm` (String, ISO 8601 datetime)
     - `versaoHomolog` (String)
     - `versaoFirebase` (String)
     - `versaoAlpha` (String)
     - `linkPlanoTestes` (String)
     - `qrCodeHomolog` (String, URL to QR code image)
     - `qrCodeAlpha` (String, URL to QR code image)
     - `tipoRelease` (String, e.g., "Exclusiva", "Normal")
     - `plataforma` (String, e.g., "Android", "iOS")

2. `SquadsModulos` Table:
   - Primary Key: `squadModuloId` (String, UUID)
   - Attributes:
     - `squad` (String)
     - `modulo` (String)
     - `detalheEntrega` (String)
     - `responsavel` (String)
     - `status` (String, e.g., "concluído", "em andamento", "bloqueado", "concluido com bugs")
     - `reportarBug` (String, text field for bug details)
     - `regressivoId` (String, Foreign Key to `Regressivos` table)

3. `Configuracoes` Table:
   - Primary Key: `configuracaoId` (String, e.g., "squads_e_modulos")
   - Attributes:
     - `data` (JSON String, to store the squads.json content)


AWS Services:
- **DynamoDB**: For storing application data (Regressivos, SquadsModulos, Configuracoes).
- **Lambda**: For backend API logic (CRUD operations, SLA management, Release Notes generation).
- **API Gateway**: To expose Lambda functions as RESTful APIs for the frontend.
- **S3**: For hosting the static frontend application and storing QR code images.
- **IAM**: For managing permissions for Lambda, DynamoDB, S3, and other AWS services.
- **CloudWatch**: For logging and monitoring Lambda functions and API Gateway.
- **Gemini API**: For generating Release Notes (accessed via Lambda).


