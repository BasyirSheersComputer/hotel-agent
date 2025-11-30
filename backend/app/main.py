app = FastAPI(title="Club Med Resort Genius API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all. In production, restrict to frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Club Med Resort Genius API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
