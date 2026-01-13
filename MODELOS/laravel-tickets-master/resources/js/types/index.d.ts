export interface User {
    id: number | string;
    avatar: string;
    name: string;
    role: string;
    email: string;
    password: string;
    email_verified_at: string;
    permissions: string[];
    can: (permission: string) => boolean
}

export type PageProps<T extends Record<string, unknown> = Record<string, unknown>> = T & {
    auth: {
        user: User;
    };
    status?: string;
};

export interface Pagination {
    meta: {
        current_page: number,
        from: number,
        last_page: number,
        links: Array<{ url: string | null, label: string, active: boolean }>;
        path: string,
        per_page: number,
        to: number,
        total: number,
    };
}

export interface Comment {
    id: number | string;
    message: string;
    user_id: number | string
    ticket_id: number | string;
    user: User;
    ticket: Ticket;
    created_at: string
}

export interface Ticket {
    id: number | string;
    ticket_number: string;
    title: string;
    description: string;
    status: string;
    created_at: string;
    user_id: string | number;
    category_id: string | number;
    user: User;
    category: Category;
    assignedUsers: User[];
    assignedTeams: Team[]
    comments: Comment[];
}

export interface Team {
    id: number | string;
    name: string;
    manager_id: number | string;
    manager: User;
    description: string;
    created_at: string;
    users?: User[],
    categories?: Category[]
}

export interface Category {
    id: number | string;
    name: string;
    description: string;
    category_id: string | number;
    created_at: string;
    category?: Category
}

export interface FlashMessages {
    success?: string;
    error?: string;
    status?: string;
    message?: string;
}
