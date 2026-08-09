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
function startDebate() {

    const question =
        document.getElementById("question").value.trim();

    if (question === "") {

        alert("Please enter a business question.");

        return;
    }


    document.getElementById("ceo-opinion").innerText =
        "From a strategic perspective, this decision should support the company's long-term growth.";

    document.getElementById("cfo-opinion").innerText =
        "The financial impact should be carefully evaluated before making the decision.";

    document.getElementById("sales-opinion").innerText =
        "This decision could improve sales if it creates additional customer value.";

    document.getElementById("hr-opinion").innerText =
        "The impact on employees and the organization's ability to execute the plan should be considered.";

    document.getElementById("final-result").innerText =
        "The board recommends evaluating the decision using financial, sales, strategic and employee perspectives before implementation.";

}