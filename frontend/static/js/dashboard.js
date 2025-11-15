import { apiCreateListing } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("create-listing-form");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        const payload = {
            title: formData.get("title"),
            price: Number(formData.get("price")),
        };

        try {
            await apiCreateListing(payload);

            alert("Listing created!");

            // Close modal via Flowbite
            document.querySelector('[data-modal-toggle="createListingModal"]').click();

            form.reset();
            location.reload(); // refresh dashboard (or you can dynamically insert into DOM)
        } catch (err) {
            alert("Error: " + err.message);
        }
    });
});