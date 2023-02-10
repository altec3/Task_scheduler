from rest_framework.routers import Route, SimpleRouter


class CustomAPIRouter(SimpleRouter):
    """Маршрутизатор для выполнения требований к структуре URL проекта"""

    routes = [
        #: Create route.
        Route(
            url=r'^{prefix}/create{trailing_slash}$',
            mapping={'post': 'create'},
            name='{basename}-create',
            detail=False,
            initkwargs={'suffix': 'Create'}
        ),
        #: List route.
        Route(
            url=r'^{prefix}/list{trailing_slash}$',
            mapping={'get': 'list'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        #: Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
    ]
