# Product pricing

Product price tiers are generated from price rules configured for each sales
department (new in v3.0). These tiers are used in deals to calculate item amounts
automatically. The calculation uses the product's price tier, the deal
currency, the quantity, and any additional discount applied to the deal item.
The price is converted to the deal currency when the amount is calculated.

You can export price lists for all products or selected products to an Excel workbook.
The workbook has a separate worksheet for each product category; products without a category are placed on a worksheet named **Without category**.

## Departments, products, and categories

Django CRM supports multiple sales departments.
Each department can maintain its own products and services, and products can be assigned to categories.
First, [add product categories and products](adding_products_and_services.md), and assign each product to the appropriate department and category.

## Configure department price rules

Create price rules in each sales department's settings.
Set the department's default currency and define a rule for each price tier.
Each department must have one base tier. Its price type is **Fixed Price**.
The other tiers are calculated from the base tier, and all non-base rules in a department must use the same price type.

For example, configure these department rules:

| Price tier | Price type | Percentage |
|---|---|---:|
| end customer | Fixed Price; select **Base tier** | — |
| reseller | Discount percentage | 10 |
| dealer | Discount percentage | 20 |
| distributor | Discount percentage | 30 |

The available price types are **Fixed Price**, **Discount percentage**, and **Markup percentage**.
For discount and markup rules, enter the percentage relative to the base price.

## Configure category price rules

After creating the department price rules, you can add **Price Rules** as inline
items when editing a product category. Category rules can adjust the price
tiers for products in that category and take precedence over the department's
rules. The category rule tier choices are limited to tiers already configured
for the category's department.

## Add price tiers to products

After configuring the rules:

1. Open a product and make sure it is assigned to a department.
2. Use **Add Price Tier** to create the base price tier. If the product has no price tiers yet, CRM creates the base tier with a zero price.
3. Enter the base price in the **Product Price Tiers** section. The currency shown for the price tier is the department's default currency.
4. Use **Add Price Tier** again. CRM creates the remaining price tiers according to the applicable department or category rules.

For a base price of 100, the example rules above produce these prices:

| Price tier | Price |
|---|---:|
| end customer | 100 |
| reseller | 90 |
| dealer | 80 |
| distributor | 70 |

Price tiers can also include additional information, such as a minimum quantity, validity dates, and a description.

## Amounts in deals

When a product is added to a deal, CRM calculates its amount using the selected price tier and quantity,
converts the price to the deal's currency, and applies any additional discount specified for the deal item.
The amount is recalculated when relevant values change, such as the deal currency, price tier, quantity, or discount.
A deal discount can be a fixed value or a percentage.

## Export price lists

On the products page, select the products to include (or apply the action to all products),
then choose **Export price lists to Excel** from the **Action** menu.
The workbook contains the available price tiers for the selected products, grouped into separate worksheets by category.
