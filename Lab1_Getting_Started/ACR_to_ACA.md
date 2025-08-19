## ACR (Azure Container Registry) to ACA (Azure Container Apps)

![ACR_to_ACA](./Assets/ACR_to_ACA.png)

### Create a Container Apps Environment
We will now create a container apps environment that will host our Container App.

Follow the steps laid down in the visuals below:
![aca_select](./Assets/aca_select.png)
--
![create_new_aca_env](./Assets/create_new_aca_env.png)
--
![create_aca_env](./Assets/create_aca_env.png)

### Create a Container App
Now we will create a container app inside the newly create container app environment that will host our image that is contained in our Azure Container Registry. 

![aca_app_name](./Assets/aca_app_name.png)
--
![aca_container_details_1](./Assets/aca_container_details_1.png)
--
![aca_container_details_2](./Assets/aca_container_details_2.png)
--
![ingress_config](./Assets/ingress_config.png)

### Accessing our Chat Application
Once your container app gets provisioned, you can go to the `Revisions and replicas` tab to view the Application's FQDN, navigating to which will lead you to land on your chat application's homepage.

![view_randr](./Assets/view_randr.png)
--
![copy_FQDN](./Assets/copy_FQDN.png)
--
![application_homepage](./Assets/application_homepage.png)

You can also view the logs of the running revision of your container app:
![view_logs](./Assets/view_logs.png)

## Summary
In this lab, we successfully deployed a containerized chat application from Azure Container Registry (ACR) to Azure Container Apps (ACA). We created a container apps environment, set up a container app, and configured the necessary settings to ensure our application runs smoothly. Finally, we accessed our application and verified its functionality.
