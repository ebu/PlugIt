# HowTo: Subscriptions

The point of this document is to explain how to retrieve and use subscription labels.

## EBU.io Subscriptions

EBU.io platform offers the users to manage subscription for PlugIt Projects. PlugIt Developers can access the subscriptions 
using the PlugIt API or the `subscription_labels` user_info decorator.

If a user has a valid subscription to a given subscription plan (defined by a plan label) the api will return this label
in the subscription endpoint.

## Example

The following flask method describes how you may access the subscriptions

    @action(route="/page", template="page/home.html")
    @user_info(['pk'])
    @only_orga_member_user()
    def page_home(request):
        """Show the home page."""
    
        # Instantiate a plugit API object
        plugitapi = PlugItAPI(config.API_URL)
        
        # Get the users Primary Key out of the request data
        userPk = request.args.get('ebuio_u_pk') or request.form.get('ebuio_u_pk')
        
        # Retrieve the subscriptions from the API
        subs = plugitapi.get_subscription_labels(userPk)
        
        ...
        
        
Or use the decorator to retrieve the subscriptions directly

    @action(route="/page", template="page/home.html")
    @user_info(['subscription_labels', 'pk'])
    @only_orga_member_user()
    def stations_home(request):
        """Show the home page."""
    
        # Instantiate a plugit API object
        plugitapi = PlugItAPI(config.API_URL)
        
        # Get the subscription labels directly from the arguments of the request
        subs = request.args.get('ebuio_u_subscription_labels') or request.form.get('ebuio_u_subscription_labels')
        
        ...


Note: the subscription list is cached on the EBU.io platform, thus requesting it multiple times should not significantly
delay your requests
