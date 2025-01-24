# MySQL Container for Your Django CRM Database

In the project inside `docker` folder you can find files necessary to provide a streamlined approach to setting up a MySQL container for your Django CRM database, drawing inspiration from the well-regarded project.

### Key Benefits  

- **Simplified Database Management:**  
  Benefit from the ease and efficiency of containerized databases. MySQL containers offer a self-contained environment, simplifying deployment and management.
- **Scalability and Flexibility:**  
  Scale your database resources effortlessly as your Django CRM application grows. Containers provide a lightweight and portable solution that adapts to your needs.
- **Improved Development Workflow:**  
  Streamline your development process with a readily available database environment. This setup facilitates rapid testing and iteration.
- **Clear and Concise Instructions:**  
  The repository includes clear instructions to guide you through the setup process, ensuring a smooth and successful deployment.

### Getting Started

- **Prerequisites:**  
  Docker: Ensure you have Docker installed on your system. Refer to the official [Docker documentation](https://docs.docker.com/get-docker/) for installation instructions.
- **Docker Compose:**  
  Install Docker Compose using the instructions provided [here](https://docs.docker.com/compose/install/).
  
- **Build and Run the Containers:**  
  copy the docker folder inside Django-CRM project folder.  
  Run `Bash:`  
  `./start_dev.sh`  
  This command will build the necessary Docker images and start the MySQL container in detached mode (-d).  
  It also:  
  - Install requirements
  - Fill initial data into database
  - Start the application

- **Check your Django CRM settings:**  
  Verify your Django-CRM application's database configuration settings to point to the MySQL container.  
  In `webcrm/settings.py` `'HOST'` should be `'127.0.0.1'`.  
  Refer to your Django project's documentation for specific instructions on configuring database connections.

### Additional Considerations

- **Security:**  
  Prioritize security by implementing appropriate authentication and authorization mechanisms for your MySQL container. Consider using environment variables to store sensitive database credentials.
- **Persistence:**  
  If you require data persistence beyond the container's lifecycle, explore volume mounting techniques to store database data on your host system.
- **Customization:**  
  This repository serves as a foundation. Feel free to customize the Dockerfile and docker-compose.yml files to tailor the setup to your specific requirements.

### Community and Support

For questions or assistance, feel free to raise issues on this repository or connect with the Django community for further guidance.

### Contributing

We welcome contributions to this project! If you have improvements or suggestions, please submit pull requests.

By following these steps and considerations, you can effectively leverage a MySQL container to manage your Django CRM database, enhancing your development experience and application's scalability.
