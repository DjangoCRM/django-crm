## Guide for company executives

By default, company executives have access to all sections. 
If some sections or objects are not of interest, they can be hidden using individual settings - 
contact your Django-CRM administrator.

!!! Important

    #### Access and Permissions  
    
    - Default access to the Analytics app is granted to company executives, sales managers, and CRM administrators.  


### CRM Analytics

The **Analytics app** in this [eCRM software](https://github.com/DjangoCRM/django-crm/){target="_blank"} provides comprehensive statistical and analytical reports 
to help users gain insights into their business operations. 
This app is designed to assist company executives and sales managers, 
in making data-driven decisions by offering various reports and visualizations.

#### Analytical Reports  

Reports include both tabular and graphical representations for intuitive data interpretation.

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png){target="_blank"}
##### Income Summary Report

   *  Details monthly [deal](guide_for_sales_manager.md#deal-object) income, product sales, and payment volumes.
   *  Forecasts payments for the current and upcoming two months, 
      categorized into guaranteed, high-probability, and low-probability payments.
   * Includes visualizations such as:

       * Last 12 months' income trends  
       * Income comparison for the same period in the previous year  
       * 12-month cumulative income analysis

##### Sales Funnel Report

   - Visualizes sales stages, pinpointing bottlenecks and areas for process optimization.  

##### Sales Report

   - Summarizes performance metrics like total sales, average deal size, and other key indicators over specified periods.  

##### Requests Summary

   - Tracks commercial inquiries, including [request](operator_and_sales_manager_roles.md#working-with-requests) counts, statuses, and conversion rates.  

##### Lead Source Summary

   - Evaluates the effectiveness of [lead](operator_and_sales_manager_roles.md#lead-object) sources, identifying those driving the most leads and conversions.  

##### Conversion Summary

   - Measures the success rate of inquiries converting into deals, highlighting improvement opportunities.  

##### Closing Reason Summary

   - Analyzes reasons for deal closures, offering insights into successful and unsuccessful outcomes.  

##### Deal Summary

   - Provides a comprehensive view of deals, including their status, value, and associated products or services.  

#### Integration and Customization  

- Fully integrated with other Django CRM modules, ensuring seamless data flow and analysis.  
- Supports customization to tailor reports to specific metrics or time frames, meeting diverse business needs.  

The Analytics app is a vital component of Django CRM, 
empowering businesses with the insights necessary to optimize customer relationships and drive strategic growth. 
With its intuitive design and powerful capabilities, it is a cornerstone for data-driven decision-making.
