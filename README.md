# AI Multi-Agent E-commerce Market Simulation System
## Architecture
![System Architecture](docs/architecture.png)
## Quick Start
### Backend (Docker)
```bash
cd deploy
docker-compose up -d
```
### Initialize System
```bash
# Run Celery initialization task
docker exec ecommerce-celery celery -A app.core.celery_app call app.tasks.simulation.initialize_system_data
```
### Frontend (Expo)
```bash
cd frontend
npm install
npx expo start
```
## Key Features
- 500 AI virtual buyers with Logistic Regression purchase prediction
- Daily simulation with macro events from a pool of 20 events
- Real-time market dashboard with price waves, hot rankings, event timeline
- AI decision explainability (feature snapshots, probability, SHAP-ready)
- Real player registration, shopping, and shop management
- Dataset cold-start support (RetailRocket / Brazilian E-Commerce)
## Project Structure
```
ecommerce-sim/
  backend/
    app/
      api/          # FastAPI route modules
      core/         # Config, database, security, celery
      models/       # SQLAlchemy models
      schemas/      # Pydantic schemas
      services/     # Business logic
      tasks/        # Celery tasks (simulation, event pool)
      ml/           # ML model (LogisticRegression), feature engineering
    scripts/
      load_dataset.py  # Data initialization from Kaggle datasets
    alembic/        # Database migrations
  frontend/
    src/
      screens/      # React Native screens
      components/   # Reusable components
      services/     # API client
      store/        # State management (AuthContext)
      navigation/   # Navigation structure
  deploy/
    docker-compose.yml
    Dockerfile
```
## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | User registration |
| POST | /api/auth/login | User login |
| GET | /api/products | Search products |
| GET | /api/products/{id} | Product detail |
| GET | /api/cart | Get cart |
| POST | /api/cart | Add to cart |
| POST | /api/orders/checkout | Checkout |
| POST | /api/orders/{id}/pay | Simulate payment |
| POST | /api/simulate/day | Trigger simulation day |
| GET | /api/market/overview | Market dashboard data |
| GET | /api/market/user/{id}/decision | AI decision explanation |
## License
MIT

## GitHub Actions — 自动构建 APK

### 一次设置，永久自动打 APK

1. **把代码推到 GitHub**（新建仓库 → git push）
2. **生成 Expo Token**：打开 https://expo.dev/settings/access-tokens → 创建 Token → 复制
3. **存到 GitHub Secrets**：仓库 Settings → Secrets and variables → Actions → New secret
   - 名称: EXPO_TOKEN
   - 值: 粘贴刚才复制的 Token
4. **手动触发构建**：仓库 Actions → Build APK → Run workflow
5. 等约 10 分钟，构建完成后在 Actions 页面下载 APK

之后每次 git push 到 main 分支也会自动构建。
