// src/hooks/useFetchData.ts
import {useState, useEffect, useCallback, useRef} from 'react';
import axios from 'axios';
import {Pagination} from "@/types";

interface PaginationData<T> extends Pagination {
    data: T[];
    links: {
        first: string,
        last: string,
        prev: string,
        next: string
    }
}

export interface FetchDataParams {
    page: number;
    search?: string;
    sort?: string;
    sortColumn?: string;
}

const useFetchData = <T,>(url: string, params: FetchDataParams) => {
    const [data, setData] = useState<T[]>([]);
    const [pagination, setPagination] = useState<Omit<PaginationData<T>, 'data'|'links'>>({
        meta: {
            current_page: 1,
            from: 1,
            last_page: 1,
            links: [],
            path: '',
            per_page: 10,
            to: 1,
            total: 1,
        }
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = useCallback(async (params: FetchDataParams) => {


        setLoading(true);
        try {
            const response = await axios.get<PaginationData<T>>(url, {
                params
            });
            setData(response.data.data);
            setPagination({
                meta: {
                    total: response.data.meta.total,
                    current_page: response.data.meta.current_page,
                    last_page: response.data.meta.last_page,
                    per_page: response.data.meta.per_page,
                    links: response.data.meta.links,
                    path: response.data.meta.path,
                    to: response.data.meta.to,
                    from: response.data.meta.from
                }
            });
            setLoading(false);
        } catch (error) {
            setError(error as Error);
            setLoading(false);
        }
    }, [url])

    useEffect(() => {
        fetchData(params);
    }, []);

    const refresh = useCallback(() => {
        fetchData(params);
    }, []);

    return { data, pagination, loading, error, refresh, fetchData };
};

export default useFetchData;
