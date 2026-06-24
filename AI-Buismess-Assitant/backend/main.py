from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, user, business, datasets, predictions, products, inventory, orders
from core.middleware import RefreshSessionMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RefreshSessionMiddleware)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(business.router)
app.include_router(datasets.router)
app.include_router(predictions.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)

# uvicorn main:app --reload
# source activate fastapi