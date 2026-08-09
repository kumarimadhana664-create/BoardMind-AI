async function predictSales() {

    const age = document.getElementById("age").value;
    const gender = document.getElementById("gender").value;
    const category = document.getElementById("category").value;
    const quantity = document.getElementById("quantity").value;
    const price = document.getElementById("price").value;

    if (!age || !quantity || !price) {
        document.getElementById("result").innerText =
            "Please enter all required values.";
        return;
    }

    try {

        const response = await fetch("/predict-sales", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                Age: Number(age),
                Gender: gender,
                "Product Category": category,
                Quantity: Number(quantity),
                "Price per Unit": Number(price)

            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed");
        }

        document.getElementById("result").innerText =
            "Predicted Sales: ₹" + data.predicted_sales;

    } catch (error) {

        console.error(error);

        document.getElementById("result").innerText =
            "Error: " + error.message;
    }
}