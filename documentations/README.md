# Transition uuidv4 To uuidv7

## Why UUIDv7 is better than UUIDv4

- UUIDv4: Fully random. Pros: low collision risk. Cons: random ordering, which fragments indexes and reduces insert performance on large tables.

- UUIDv7: Time-ordered (based on UNIX timestamp + random bits). Pros:
    - Chronological order → faster index inserts in databases (less fragmentation).
    - Still globally unique because of random suffix.
    - Makes querying by creation time easier if you ever want to derive temporal information without extra columns.

So for a high-throughput production system, UUIDv7 reduces B-tree fragmentation and improves insert performance while retaining global uniqueness.

## Implementation 

### Add a UUIDv7 Column

- Add a new column `idv7` to each table that currently uses `id`

```py
idv7 = Column(UUID(as_uuid=True), primary_key=False, index=True, unique=True, nullable=True, default=uuid.uuid7)
```

### Link Foregin Keys And Relationships

**Example**

- Users Table:

```py
class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    idv7 = Column(UUID(as_uuid=True), primary_key=False, index=True, unique=True, nullable=True, default=uuid.uuid7)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Foreign key to Subscriptions table
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    subscription_idv7 = Column(UUID(as_uuid=True), ForeignKey("subscriptions.idv7"), nullable=True)

    subscription_started_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    subscription_expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(days=365*50))

    current_environments = Column(Integer, nullable=True, default=0)
    current_scans_per_month = Column(Integer, nullable=True, default=0)

    verified = Column(Boolean, default=False, nullable=False)

    # Relationship to Subscriptions
    subscription = relationship("Subscriptions", back_populates="users", foreign_keys=[subscription_id])
    subscription_v7 = relationship("Subscriptions", back_populates="users_v7", foreign_keys=[subscription_idv7], primaryjoin="Users.subscription_idv7 == Subscriptions.idv7")
    
    # Relationship to Environments
    environments = relationship("Environments", back_populates="users", foreign_keys="Environments.user_id", cascade="all, delete-orphan")
    environments_v7 = relationship("Environments", back_populates="users_v7", foreign_keys="Environments.user_idv7", primaryjoin="Users.idv7 == Environments.user_idv7", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("current_environments >= 0", name="ck_current_envs_non_negative"),
        CheckConstraint("current_scans_per_month >= 0", name="ck_current_scans_non_negative"),
    )
```

- Subscriptions Table

```py
class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    idv7 = Column(UUID(as_uuid=True), primary_key=False, index=True, unique=True, nullable=True, default=uuid.uuid7)
    name = Column(String, unique=True, nullable=False)
    price = Column(String, nullable=False)
    max_environments = Column(Integer, nullable=False)
    max_scans_per_month = Column(Integer, nullable=False)
    scan_depth = Column(Enum(ScanDepth, name="scan_depth_enum"), nullable=False)
    analysis_level = Column(Enum(AnalysisLevel, name="analysis_level_enum"), nullable=False)
    history_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Back reference
    users = relationship("Users", back_populates="subscription", foreign_keys="Users.subscription_id")
    users_v7 = relationship("Users", back_populates="subscription_v7", foreign_keys="Users.subscription_idv7", primaryjoin="Subscriptions.idv7 == Users.subscription_idv7")
```

### Primary Join

When you have dual relationships with UUIDv7 columns, you should include primaryjoin. Otherwise, SQLAlchemy can get confused and still try to match the original v4 column by default.

### Dual Read/Write Operations

During the transition, your application code (repositories, services) should read/write to both the original `id` and the new `idv7` columns. This ensures that new records get UUIDv7 while existing records remain accessible.

**Example**

```py
def get_current_environment(self, users_id: str):
    return (
        self.db.query(Users.current_environments)
        .filter(or_(Users.id == users_id, Users.idv7 == users_id))
        .scalar()
    )
```

### Alembic Migration

generate a new Alembic migration to add the `idv7` column to each table, and then run the migration.

```py
"""add uuidv7 transition columns

Revision ID: 20260325_01
Revises:
Create Date: 2026-03-25 11:55:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260325_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subscriptions", sa.Column("idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_subscriptions_idv7", "subscriptions", ["idv7"])
    op.create_index("ix_subscriptions_idv7", "subscriptions", ["idv7"], unique=False)

    op.add_column("users", sa.Column("idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("users", sa.Column("subscription_idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_users_idv7", "users", ["idv7"])
    op.create_index("ix_users_idv7", "users", ["idv7"], unique=False)
    op.create_foreign_key(
        "fk_users_subscription_idv7_subscriptions",
        "users",
        "subscriptions",
        ["subscription_idv7"],
        ["idv7"],
    )

    op.add_column("environments", sa.Column("idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("environments", sa.Column("user_idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_environments_idv7", "environments", ["idv7"])
    op.create_index("ix_environments_idv7", "environments", ["idv7"], unique=False)
    op.create_index("ix_environments_user_idv7", "environments", ["user_idv7"], unique=False)
    op.create_unique_constraint("uix_user_environment_name_v7", "environments", ["name", "user_idv7"])
    op.create_foreign_key(
        "fk_environments_user_idv7_users",
        "environments",
        "users",
        ["user_idv7"],
        ["idv7"],
    )

    op.add_column("scans", sa.Column("idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("scans", sa.Column("environment_idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_scans_idv7", "scans", ["idv7"])
    op.create_index("ix_scans_idv7", "scans", ["idv7"], unique=False)
    op.create_index("ix_scans_environment_idv7", "scans", ["environment_idv7"], unique=False)
    op.create_unique_constraint("uix_environment_scan_name_v7", "scans", ["scan_name", "environment_idv7"])
    op.create_foreign_key(
        "fk_scans_environment_idv7_environments",
        "scans",
        "environments",
        ["environment_idv7"],
        ["idv7"],
    )

    op.add_column("blacklisted_tokens", sa.Column("idv7", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_blacklisted_tokens_idv7", "blacklisted_tokens", ["idv7"])
    op.create_index("ix_blacklisted_tokens_idv7", "blacklisted_tokens", ["idv7"], unique=False)

    # Transitional backfill: mirror existing v4 IDs into v7 columns so dual-read/write works immediately.
    op.execute("UPDATE subscriptions SET idv7 = id WHERE idv7 IS NULL")
    op.execute("UPDATE users SET idv7 = id WHERE idv7 IS NULL")
    op.execute("UPDATE users SET subscription_idv7 = subscription_id WHERE subscription_idv7 IS NULL")
    op.execute("UPDATE environments SET idv7 = id WHERE idv7 IS NULL")
    op.execute("UPDATE environments SET user_idv7 = user_id WHERE user_idv7 IS NULL")
    op.execute("UPDATE scans SET idv7 = id WHERE idv7 IS NULL")
    op.execute("UPDATE scans SET environment_idv7 = environment_id WHERE environment_idv7 IS NULL")
    op.execute("UPDATE blacklisted_tokens SET idv7 = id WHERE idv7 IS NULL")


def downgrade() -> None:
    op.drop_index("ix_blacklisted_tokens_idv7", table_name="blacklisted_tokens")
    op.drop_constraint("uq_blacklisted_tokens_idv7", "blacklisted_tokens", type_="unique")
    op.drop_column("blacklisted_tokens", "idv7")

    op.drop_constraint("fk_scans_environment_idv7_environments", "scans", type_="foreignkey")
    op.drop_constraint("uix_environment_scan_name_v7", "scans", type_="unique")
    op.drop_index("ix_scans_environment_idv7", table_name="scans")
    op.drop_index("ix_scans_idv7", table_name="scans")
    op.drop_constraint("uq_scans_idv7", "scans", type_="unique")
    op.drop_column("scans", "environment_idv7")
    op.drop_column("scans", "idv7")

    op.drop_constraint("fk_environments_user_idv7_users", "environments", type_="foreignkey")
    op.drop_constraint("uix_user_environment_name_v7", "environments", type_="unique")
    op.drop_index("ix_environments_user_idv7", table_name="environments")
    op.drop_index("ix_environments_idv7", table_name="environments")
    op.drop_constraint("uq_environments_idv7", "environments", type_="unique")
    op.drop_column("environments", "user_idv7")
    op.drop_column("environments", "idv7")

    op.drop_constraint("fk_users_subscription_idv7_subscriptions", "users", type_="foreignkey")
    op.drop_index("ix_users_idv7", table_name="users")
    op.drop_constraint("uq_users_idv7", "users", type_="unique")
    op.drop_column("users", "subscription_idv7")
    op.drop_column("users", "idv7")

    op.drop_index("ix_subscriptions_idv7", table_name="subscriptions")
    op.drop_constraint("uq_subscriptions_idv7", "subscriptions", type_="unique")
    op.drop_column("subscriptions", "idv7")

```

Command to run the alembic migration

```sh
alembic upgrade head
```

### Second Migration

- Update the v7 columns to be real uuidv7 values, and then make them non-nullable.

### Third Migration

- Remove old `id` columns and rename `idv7` to `id` in each table.
- Remove all dual READ/WRITE operations from repository and service layer.

### Neo4j ScanID Transition

- Command to update the head node

```
MATCH (n)
WHERE n.scan_id = "75c5c795-5cb3-4962-a7f7-cf85f5ac203a"
SET n.scan_id = "019d24ce-cdf3-7458-a550-ebd854a85ce0"
RETURN n;
```

- Command to update the child nodes

```
MATCH (n)
WHERE n.id STARTS WITH "75c5c795-5cb3-4962-a7f7-cf85f5ac203a"
WITH n, split(n.id, "-") AS parts
WITH n,
     parts[-2] AS step,
     parts[-1] AS substep
SET n.id = "019d24ce-cdf3-7458-a550-ebd854a85ce0" + "-" + step + "-" + substep
RETURN count(n);
```

# Concurrency Approaches for AWS API Calls

## 1. ThreadPoolExecutor (current approach)

- You use normal boto3 (blocking)
- Run multiple API calls in parallel using threads

```py
from concurrent.futures import ThreadPoolExecutor
```

- Pros
    - Simple
    - Works reliably with boto3
    - Minimal refactor
- Cons
    - Limited scalability (threads = heavier)
    - Less efficient for large-scale enumeration

## 2. aioboto3 (async approach)

- Async version of boto3 → aioboto3
- Uses async/await instead of threads

```py
async with aioboto3.client("ec2") as ec2:
    await ec2.describe_instances()
```

- Pros
    - Much better concurrency (thousands of requests)
    - More efficient for large AWS accounts
    - Cleaner for async pipelines
- Cons
    - Requires major refactor
    - Debugging is harder
    - Some AWS services/features may behave inconsistently

## Plan: Backend Async Migration

You want full async migration for DB and AWS calls, with a single migration branch. The safest execution order is bottom-up: data layer first, then services, then routers, then validation under concurrent load.

## Migrate PostgreSQL stack to SQLAlchemy async + asyncpg.


[PostgreSQL Documentation](https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.create_async_engine)

### URL

```sh
postgresql+asyncpg://user:pass@host/db
```

### Engine

```py
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, AsyncSession=True, expire_on_commit=False)
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Endpoint Latency Before/After

### Login Endpoint 

![Before Async Latency](image.png)

# Transaction

- A transaction groups multiple queries together so that they either all succeed or all fail.
- If anything goes wrong inside the transaction, everything is rolled back automatically.
- If everything succeeds, all changes are committed at once.

# Logging

## What Each File Is For

### logging_config.py: Central logging engine.

It defines JSON format, file rotation, queue-based logging, and currently decides how exceptions are rendered.

```py
exc_type, exc_value = record.exc_info()
log_data["exception"] = f"{exc_type.__name__}: {exc_value}"
```

**Result (example)**

Instead of full traceback:

```py
"exception": "Traceback (most recent call last)..."
```

You’ll get:

```py
"exception": "DataError: can't subtract offset-naive and offset-aware datetimes"
```

### logging_middleware.py: Per-request access logging.

It adds correlation id, timing, status-based log levels, and request context fields.

### main.py: App-level exception handling boundary.
It currently handles validation errors, but not all unhandled exceptions globally.

## Correlation ID

### How to identify location using correlation_id

- Take the correlation_id from one error log line.
- Search all log lines with that same id in app.log.
- Read them by timestamp to reconstruct request flow.
- Use these fields in each line:
    - logger: tells layer (access/main/service)
    - path + method: tells endpoint
    - file + function: tells where that log was emitted
    - error/error_type: tells failure reason

**Important:** correlation_id links events; actual bug location is inferred from the related log fields and endpoint code path.

# Paddle Payment Integration

## Create Product in Paddle

First we have to create products in paddle with prices and billing cycles that match our subscription plans. This will give us product IDs and price IDs to use in our backend.

## Enable Webhook 

We need to setup webhooks so paddle can communicate with our backend. When the user subscribes, cancels, or updates their subscription, paddle will send a webhook to our endpoint with the details. We need to handle these webhooks to update our database accordingly.

### Ngrok

if we are working on local development, we can use ngrok to create a secure tunnel to our localhost. This will allow paddle to send webhooks to our local machine for testing.

Start our application on localhost (e.g., http://localhost:8000) and then run ngrok:

```sh
ngrok http 8000
```

Copy the Forwarding URL provided by ngrok (e.g., https://abcd1234.ngrok.io) and set it as the webhook URL in the Paddle dashboard.

![Webhook](image-1.png)

## Create Webhook Endpoint

We need to create an endpoint in our FastAPI application to receive webhook events from Paddle. This endpoint will listen for POST requests and process the incoming data.

```py
async def webhook_handler(self, request: Request):
    raw_body = await request.body()

    signature = request.headers.get("Paddle-Signature", "")
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Paddle-Signature header")
    
    if not self.paddle.verify_paddle_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    payload = await request.form()

    event_type = payload["event_type"]

    print(f"Received Paddle webhook: {event_type}")

    return {"ok": True}
```

It will verifes the signature to ensure the request is from Paddle, then processes the payload based on the event type (e.g., subscription created, subscription cancelled).

## The Working

The general flow is:
1. User clicks "Subscribe" on frontend → sends request to backend to create a transaction. It will return a checkout URL from Paddle.
2. User completes checkout on Paddle → Paddle sends webhook to our backend with subscription details.
3. Backend processes webhook → updates user subscription status and details in database.

### Tunneling

I have to tunnel both frontend and backend using ngrok to test the full flow locally, since Paddle needs to communicate with our backend via webhooks.

## Renew Logic

The user subscribe on 14 Aug so the subscribe should end next month at the end of the day not at the time when he subscribe.

```py
def calculate_expiry(started_at: datetime) -> datetime:
    # Move to next month same day
    next_month = started_at + relativedelta(months=1)

    # Set to end of that day (23:59:59)
    expires_at = next_month.replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    return expires_at
```

### Important edge cases

**What if:**
- user subscribes on 31 Jan

**Next month:**
- Feb doesn’t have 31

**relativedelta handles this:**

→ becomes 28 Feb / 29 Feb

### Renewals

**When user renews:**

```sh
new_expiry = calculate_expiry(current_expiry)
```

NOT from now — otherwise users lose remaining time.

# Browsers List

## Why it matters

### If not updated:

- You might support wrong browser versions
- Miss new browser changes
- Ship unnecessary or missing CSS prefixes

```sh
npx update-browserslist-db@latest
```

# ACID Properties

## Atomicity

- All operations in a transaction succeed or fail together.

### Example

```py
# Create new user
user = await self.user_repo.create_user(user.email, hashed_password)

# Get default "Free" subscription plan ID
plan_id = await self.subs_repo.get_plan_id("Free")

# Link default plan to new user
subscription = await self.subs_repo.create_subscription(user.id, plan_id)
```

Currently all operations are operating independently. If the subscription creation fails after user creation, we end up with a user without a subscription, which is an inconsistent state.

### Solution

- Wrap in a DB transaction

```py
try:
    async with self.db.begin():
        # Create new user
        user = await self.user_repo.create_user(user.email, hashed_password)
        
        # Get default "Free" subscription plan ID
        plan_id = await self.subs_repo.get_plan_id("Free")
        if not plan_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default subscription plan is not configured"
            )

        # Link default plan to new user
        await self.subs_repo.create_subscription(user.id, plan_id)
    return user
except HTTPException:
    raise
except Exception:
    logger.exception("Registration failed")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An error occurred during registration. Please try again later."
    )
```

# Redis Caching

## Install

```sh
brew install redis
brew services start redis
```

## In FastAPI

```sh
pip install "redis[hiredis]" aioredis
```

## Usage


### redis/dependency.py

```py
import redis.asyncio as redis
from app.utils import settings

# Global Redis pool
redis_pool: redis.Redis = None

async def get_redis() -> redis.Redis:
    return redis_pool

async def init_redis():
    global redis_pool
    redis_pool = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    await redis_pool.aclose()
```

### utils/dependency/depencies.py

make a dependency for Redis that can be injected into routes and services

```py
Redis = Annotated[redis.Redis, Depends(get_redis)]
```

### utils/redis_helper.py

```py
async def get_cached(cache, key: str) -> dict | None:
    if not cache:
        return None
    try:
        cached = await cache.get(key)
        if cached:
            return json.loads(cached)
    except (Exception, json.JSONDecodeError) as e:
        logger.warning(f"Cache read failed for {key}: {e}")
    return None

async def set_cached(cache, key: str, data: dict) -> None:
    if not cache:
        return
    try:
        await cache.setex(key, settings.REDIS_TTL, json.dumps(data))
    except Exception as e:
        logger.warning(f"Cache write failed for {key}: {e}")
```