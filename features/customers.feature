Feature: The customer service back-end
    As a Customer Service Manager
    I need a RESTful catalog service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | first_name | last_name | address                        | suspended |
        | John       | Doe       | 123 Main St, New York, NY      | False     |
        | Jane       | Smith     | 456 Oak Ave, Los Angeles, CA   | False     |
        | Bob        | Johnson   | 789 Pine Rd, Chicago, IL       | True      |
        | Alice      | Williams  | 321 Elm St, Houston, TX        | False     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customers Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Michael"
    And I set the "Last Name" to "Brown"
    And I set the "Address" to "555 Broadway, Boston, MA"
    And I select "False" in the "Suspended" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "Address" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Michael" in the "First Name" field
    And I should see "Brown" in the "Last Name" field
    And I should see "555 Broadway, Boston, MA" in the "Address" field
    And I should see "False" in the "Suspended" dropdown

Scenario: List all customers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John" in the results
    And I should see "Jane" in the results
    And I should see "Bob" in the results

Scenario: Search for customers by last name
    When I visit the "Home Page"
    And I set the "Last Name" to "Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John" in the results
    And I should not see "Jane" in the results
    And I should not see "Bob" in the results

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "John"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John" in the "First Name" field
    And I should see "Doe" in the "Last Name" field
    When I change "Address" to "999 New Address, Miami, FL"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "999 New Address, Miami, FL" in the "Address" field

Scenario: Suspend a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Jane"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane" in the "First Name" field
    When I copy the "Id" field
    And I press the "Suspend" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "True" in the "Suspended" dropdown

Scenario: Unsuspend a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Bob"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Bob" in the "First Name" field
    And I should see "True" in the "Suspended" dropdown
    When I copy the "Id" field
    And I press the "Unsuspend" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "False" in the "Suspended" dropdown

