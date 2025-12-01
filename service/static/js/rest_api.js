$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_address").val(res.address);
        // Convert boolean/string to "True"/"False" to match dropdown options
        let suspended_value = (res.suspended === true || res.suspended === "true" || res.suspended === "True") ? "True" : "False";
        $("#customer_suspended").val(suspended_value);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_address").val("");
        $("#customer_suspended").val("False");
    }

    // Updates the flash message area
    function flash_message(message, type = "success") {
        $("#flash_message").empty();
        $("#flash_message").removeClass();
        $("#flash_message").addClass("alert alert-" + type);
        $("#flash_message").text(message);
        $("#flash_message").show();
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let address = $("#customer_address").val();
        let suspended = $("#customer_suspended").val() === "True";

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "suspended": suspended
        };

        $("#flash_message").empty();
        
        let ajax =         $.ajax({
            type: "POST",
            url: "/api/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger");
        });
    });


    // ****************************************
    // Retrieve a Customer
    // ****************************************

    $("#retrieve-btn").click(function () {
        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/customers/${customer_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            clear_form_data();
            flash_message(res.responseJSON.message, "danger");
        });
    });

    // ****************************************
    // Update a Customer
    // ****************************************

    $("#update-btn").click(function () {
        let customer_id = $("#customer_id").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let address = $("#customer_address").val();
        let suspended = $("#customer_suspended").val() === "True";

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "suspended": suspended
        };

        $("#flash_message").empty();

        let ajax =         $.ajax({
            type: "PUT",
            url: `/api/customers/${customer_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger");
        });
    });

    // ****************************************
    // Delete a Customer
    // ****************************************

    $("#delete-btn").click(function () {
        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax =         $.ajax({
            type: "DELETE",
            url: `/api/customers/${customer_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            flash_message("Customer has been Deleted!");
        });

        ajax.fail(function(res){
            flash_message("Server error!", "danger");
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        clear_form_data();
        $("#flash_message").empty();
    });

    // ****************************************
    // Search for Customers
    // ****************************************

    $("#search-btn").click(function () {
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let address = $("#customer_address").val();

        let queryString = "";

        if (first_name) {
            queryString += 'first_name=' + first_name;
        }
        if (last_name) {
            if (queryString.length > 0) {
                queryString += '&last_name=' + last_name;
            } else {
                queryString += 'last_name=' + last_name;
            }
        }
        if (address) {
            if (queryString.length > 0) {
                queryString += '&address=' + address;
            } else {
                queryString += 'address=' + address;
            }
        }

        $("#flash_message").empty();

        let ajax =         $.ajax({
            type: "GET",
            url: `/api/customers?${queryString}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">ID</th>';
            table += '<th class="col-md-2">First Name</th>';
            table += '<th class="col-md-2">Last Name</th>';
            table += '<th class="col-md-3">Address</th>';
            table += '<th class="col-md-1">Suspended</th>';
            table += '<th class="col-md-2">Actions</th>';
            table += '</tr></thead><tbody>';
            let firstCustomer = "";
            for(let i = 0; i < res.length; i++) {
                let customer = res[i];
                table +=  `<tr id="row_${i}">
                    <td>${customer.id}</td>
                    <td>${customer.first_name}</td>
                    <td>${customer.last_name}</td>
                    <td>${customer.address}</td>
                    <td>${customer.suspended}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick='retrieve_customer("${customer.id}")'>Edit</button>
                    </td>
                </tr>`;
                if (i === 0) {
                    firstCustomer = customer;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstCustomer !== "") {
                update_form_data(firstCustomer);
            }

            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger");
        });
    });

    // ****************************************
    // Suspend a Customer
    // ****************************************

    $("#suspend-btn").click(function () {
        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax =         $.ajax({
            type: "PUT",
            url: `/api/customers/${customer_id}/suspend`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger");
        });
    });

    // ****************************************
    // Unsuspend a Customer
    // ****************************************

    $("#unsuspend-btn").click(function () {
        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax =         $.ajax({
            type: "PUT",
            url: `/api/customers/${customer_id}/unsuspend`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger");
        });
    });
});

// ****************************************
// Retrieve a Customer (for table button)
// ****************************************

function retrieve_customer(customer_id) {
    let ajax = $.ajax({
        type: "GET",
        url: `/api/customers/${customer_id}`,
        contentType: "application/json",
        data: ''
    });

    ajax.done(function(res){
        $("#customer_id").val(res.id);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_address").val(res.address);
        // Convert boolean/string to "True"/"False" to match dropdown options
        let suspended_value = (res.suspended === true || res.suspended === "true" || res.suspended === "True") ? "True" : "False";
        $("#customer_suspended").val(suspended_value);
        
        $("#flash_message").removeClass();
        $("#flash_message").addClass("alert alert-success");
        $("#flash_message").text("Success");
        $("#flash_message").show();
    });

    ajax.fail(function(res){
        $("#flash_message").removeClass();
        $("#flash_message").addClass("alert alert-danger");
        $("#flash_message").text(res.responseJSON.message);
        $("#flash_message").show();
    });
}

