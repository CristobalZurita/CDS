    // src/components/DataTable.tsx
    import React, {useEffect, useState, useImperativeHandle, forwardRef, ForwardedRef} from 'react';
    import {BiSortAlt2} from "react-icons/bi";
    import {FaAngleLeft, FaAngleRight, FaArrowDownLong, FaArrowUpLong} from "react-icons/fa6";
    import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/Components/ui/table';
    import {Input} from '@/Components/ui/input'
    import {
        useReactTable,
        getCoreRowModel,
        getPaginationRowModel,
        getFilteredRowModel,
        getSortedRowModel,
        ColumnDef,
        flexRender, TableOptions,
    } from '@tanstack/react-table';
    import {Button} from "@/Components/ui/button";
    import {
        DropdownMenu,
        DropdownMenuCheckboxItem,
        DropdownMenuContent,
        DropdownMenuTrigger
    } from "@/Components/ui/dropdown-menu";
    import {FaAngleDown} from "react-icons/fa6";
    import {Pagination} from "@/types";
    import useFetchData, {FetchDataParams} from "@/hooks/useFetchData";

    interface DataTableProps<T> {
        columns: ColumnDef<T>[],
        data?: T[],
        fetchData?: (params: FetchDataParams) => void,
        pagination?: Pagination,
        url: string;
        getRowId: (row: T) => string;
    }

    export interface dataTableRef {
        refreshData: () => void;
    }

    const DataTable = forwardRef(<T extends { id: string | number } >({columns, url}: DataTableProps<T>, ref?: ForwardedRef<dataTableRef>) => {

        const {data, pagination, loading, error, fetchData, refresh} =
            useFetchData<T>(url, {page: 1});

        const [search, setSearch] = useState('');
        const [sort, setSort] = useState<string | undefined>();
        const [sortColumn, setSortColumn] = useState<string | undefined>()
        const [page, setPage] = useState<number>(1)


        const refreshData = () => {
            refresh()
        }

        useImperativeHandle(ref, () => ({
            refreshData
        }))

        const reFetchData = ({sort, sortColumn, search, page}: FetchDataParams) => {
            fetchData({
                page,
                sort,
                sortColumn,
                search
            });
        }

        const table = useReactTable<T>({
            data,
            columns,
            pageCount: pagination.meta.last_page,
            state: {
                pagination: {
                    pageIndex: pagination.meta.current_page - 1,
                    pageSize: pagination.meta.per_page,
                },
                sorting: sort && sortColumn ? [{id: sortColumn, desc: sort === 'desc'}] : []
            },
            manualPagination: true,
            manualSorting: true,
            getCoreRowModel: getCoreRowModel(),
            getPaginationRowModel: getPaginationRowModel(),
            getSortedRowModel: getSortedRowModel(),
            getFilteredRowModel: getFilteredRowModel(),
            onPaginationChange: (updater) => {
                const newState = typeof updater === 'function' ? updater(table.getState().pagination) : updater;
                const page = newState.pageIndex + 1
                reFetchData({page, sort, sortColumn, search});
            },
            onSortingChange: (updater) => {
                const newState = typeof updater === 'function' ? updater(table.getState().sorting) : updater;
                const sort = newState.length > 0 ? newState[0].desc ? 'desc' : 'asc' : undefined;
                const sortColumn = newState.length > 0 ? newState[0].id : undefined;
                setSort(sort);
                setSortColumn(sortColumn);
            },
            getRowId: (row) => row.id as string,
        } as TableOptions<T>);

        useEffect(() => {
            if (sort && sortColumn) {
                const page = pagination.meta.current_page;
                reFetchData({page, sort, sortColumn, search});
            }
        }, [sort, sortColumn]);

        return (
            <div className="p-4 relative">

                {loading && <div className={"absolute top-0 w-full h-full z-10 bg-background flex justify-center items-center"}>
                    <div className={""}>Loading ...</div>
                </div>}

                {error && <div className={"absolute top-0 w-full h-full z-10 bg-background flex justify-center items-center"}>
                    <div className={"text-destructive-foreground"}>{error.message}</div>
                </div>}

                <div className={"flex justify-between mb-3"}>
                    <Input
                        value={search}
                        onChange={(e) => {
                            const newSearch = e.target.value;
                            setSearch(newSearch);
                            reFetchData({page, sort, sortColumn, search: newSearch});
                        }}
                        placeholder="Search..."
                        className={"w-2/4"}
                    />

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="ml-auto">
                                Columns <FaAngleDown className="ml-2 h-4 w-4"/>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            {table
                                .getAllColumns()
                                .filter((column) => column.getCanHide())
                                .map((column) => {
                                    return (
                                        <DropdownMenuCheckboxItem
                                            key={column.id}
                                            className="capitalize"
                                            checked={column.getIsVisible()}
                                            onCheckedChange={(value) =>
                                                column.toggleVisibility(value)
                                            }
                                        >
                                            {column.id}
                                        </DropdownMenuCheckboxItem>
                                    )
                                })}
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>

                <div className={"border rounded"}>
                    <Table className={"max-w-full"}>
                        <TableHeader>
                            {table.getHeaderGroups().map(headerGroup => (
                                <TableRow key={headerGroup.id}>
                                    {headerGroup.headers.map(header => (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder ? null : (
                                                <div {...{onClick: header.column.getToggleSortingHandler()}}>
                                                    {header.column.getCanSort() ? (
                                                        <Button variant={"ghost"} className={"flex justify-between w-full"}>
                                                            {flexRender(header.column.columnDef.header, header.getContext())}
                                                            {/*<div>*/}
                                                            {/*    {header.column.getIsSorted() === 'asc' ?*/}
                                                            {/*        <FaArrowUpLong /> :*/}
                                                            {/*        <FaArrowDownLong />*/}
                                                            {/*    }*/}
                                                            {/*</div>*/}
                                                            <BiSortAlt2 className={"ms-2"}/>
                                                        </Button>
                                                    ) : flexRender(header.column.columnDef.header, header.getContext())}
                                                </div>
                                            )}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            ))}
                        </TableHeader>
                        <TableBody>
                            {table.getRowModel().rows.length ? (
                                table.getRowModel().rows.map(row => (
                                    <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                                        {row.getVisibleCells().map(cell => (
                                            <TableCell key={cell.id}
                                                       className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={columns.length} className={"h-24 text-center"}>
                                        No results.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>

                <div className="pagination flex justify-between py-4">
                    <div className={"space-x-2"}>
                        {pagination.meta.links.map(link => (
                            <Button
                                key={link.label}
                                size={"sm"}
                                variant={link.active ? "outline" : "default"}
                                onClick={() => {
                                    if (link.url) {
                                        const page = new URL(link.url).searchParams.get('page');
                                        fetchData({
                                            page: page ? parseInt(page) : 1,
                                            search,
                                            sort,
                                            sortColumn,
                                        });
                                    }
                                }}
                                disabled={!link.url || link.active}
                            >
                                {link.label.includes('Next') ? <FaAngleRight/> : link.label.includes('Previous') ?
                                    <FaAngleLeft/> : link.label}
                            </Button>
                        ))}
                    </div>
                    <span>
                      Page{' '}
                        <span>
                        {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                      </span>
                    </span>
                </div>
            </div>
        );
    });

    export default DataTable;
