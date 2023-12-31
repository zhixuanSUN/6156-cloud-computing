from fastapi import FastAPI, Response, HTTPException, Request
import uvicorn
import psycopg2
import flask

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello,buyer"}

endpoint = "database-1.ctxkoq8uo7wh.us-east-1.rds.amazonaws.com"
port = "5432"
username = "postgres"
password = "12345678"
database = "postgres"

@app.get("/getold")
async def lookup():
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM buyer")
    results = cur.fetchall()
    for row in results:
        print(row)
    cur.close()
    conn.close()
    return results

@app.get("/get")
async def lookup(buyer_id: int):
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    select_query = "SELECT * FROM buyer_buy where buyer_id = %s"
    cur.execute(select_query, (buyer_id,))
    results = cur.fetchall()
    for row in results:
        print(row)
    cur.close()
    conn.close()
    return results

@app.post("/postold")
async def add(buyer_id: int, buyer_name: str, buyer_password: str):
    if not all([buyer_id, buyer_name, buyer_password]):
        raise HTTPException(status_code=400, detail="Incomplete data provided")
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()

    select_query = "SELECT * FROM buyer WHERE buyer_id = %s"
    cur.execute(select_query, (buyer_id,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Data with the same buyer_id already exists")

    cur.execute("INSERT INTO buyer (buyer_id, buyer_name, buyer_password) VALUES (%s, %s, %s)",
                (buyer_id, buyer_name, buyer_password))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "message": "Data inserted successfully"}

@app.post("/post")
async def add(buyer_id: int, item_id: str, status: str):
    if not all([buyer_id, item_id, status]):
        raise HTTPException(status_code=400, detail="Incomplete data provided")
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()


    cur.execute("INSERT INTO buyer_buy (item_id, buyer_id, status) VALUES (%s, %s, %s)",
                (item_id, buyer_id, status))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"User:{buyer_id} add {status} Item:{item_id} to cart successfully"}

@app.delete("/deleteold")
async def delete_buyer(buyer_id: str):
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()
    delete_query = "DELETE FROM buyer WHERE buyer_id = %s"
    cur.execute(delete_query, buyer_id)

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Buyer not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "success", "message": f"Buyer with ID {buyer_id} deleted"}

@app.delete("/delete")
async def delete_buyer(buyer_id: int, item_id: int):
    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()

    cur.execute("DELETE FROM buyer_buy WHERE buyer_id = %s and item_id = %s", (buyer_id, item_id))

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Buyer not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"message": f"Buyer {buyer_id} deleted item {item_id}"}

@app.put("/putold")
async def update_password(buyer_id: int, new_password: str):

    if not new_password:
        raise HTTPException(status_code=400, detail="New password is required")

    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()

    select_query = "SELECT * FROM buyer WHERE buyer_id = %s"
    cur.execute(select_query, (buyer_id,))

    existing_data = cur.fetchone()
    if not existing_data:
        raise HTTPException(status_code=404, detail="Buyer not found")

    update_query = "UPDATE buyer SET buyer_password = %s WHERE buyer_id = %s"
    cur.execute(update_query, (new_password, buyer_id))
    conn.commit()

    cur.close()
    conn.close()

    return {"status": "success", "message": f"Password updated for buyer with ID {buyer_id}"}

@app.put("/put")
async def update_password(buyer_id: int, item_id: int, status: int):

    conn = psycopg2.connect(
        host=endpoint,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cur = conn.cursor()


    update_query = "UPDATE buyer_buy SET status = %s WHERE buyer_id = %s and item_id = %s"
    cur.execute(update_query, (status, buyer_id, item_id))
    conn.commit()

    cur.close()
    conn.close()

    return {"message": f"Buyer {buyer_id} change the quantity of item {item_id} to {status}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
