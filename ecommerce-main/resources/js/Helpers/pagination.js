import { router } from '@inertiajs/vue3';

export const handlePagination = (event, routeName, resourceName) => {
    const page = (event.first / event.rows) + 1;
    router.get(routeName, {
        page: page,
        per_page: event.rows
    }, {
        preserveState: true,
        preserveScroll: true,
        only: ['items']
    });
};
