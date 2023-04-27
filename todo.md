# Todo

-   presentation

    -   make graph

-   local env

    -   STAGE based on branch

-   code cleanup

    -   make static vars dynamic

-   github

    -   https://github.com/actions/checkout#Push-a-commit-using-the-built-in-token
    -   setup graph change deploy
    -   setup serverless change deploy
    -   frontend deploy s3
    -   tests
        -   auth
        -   detection

-   webui

    -   copy token widget

-   tf
    -   setup / test backend github actions deploy role
        -   https://dav009.medium.com/serverless-framework-minimal-iam-role-permissions-ba34bec0154e

# Complete

-   local env

    -   .in

-   tf

    -   setup cognito
    -   s3 cloudfront
    -   dynamobdb
    -   setup deploy role
    -   setup exec role
    -   sns topic

-   webui

    -   setup
    -   grid
    -   configurable selection of grid
    -   stage
    -   websocket grid handler

-   backend
    -   lambdas
        -   websocket
            -   https://github.com/lgoodridge/serverless-chat/blob/master/backend/serverless.yml
            -   https://github.com/lgoodridge/serverless-chat/blob/master/backend/handler.py
        -   token handling auth https://github.com/claytantor/serverless-cognito-api/blob/master/auth.py
        -   serverless offline https://www.serverless.com/plugins/serverless-offline#websocket
        -   sns handling for dynamodb triggers

*   dynamodb (ORM)
    -   table structure
    -   user state, based on cognito id
