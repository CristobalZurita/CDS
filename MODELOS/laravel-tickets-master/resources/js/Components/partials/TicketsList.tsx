import React from 'react';
import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps} from "@/types";
import DataTable from "@/Components/DataTable";
import useColumns from "@/lib/dt-columns/tickets";
import {Button} from "@/Components/ui/button";
import {FaPlus} from "react-icons/fa6";

function TicketsList({ auth }: PageProps) {

    const columns = useColumns();

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">My Tickets</h2>

                    {auth.user.permissions.includes('create_tickets') && <Link href={route('tickets.create')}>
                        <Button size={"sm"}>
                            <FaPlus className={"me-2"} />
                            <span>Create Ticket</span>
                        </Button>
                    </Link>}
                </div>
            }
        >
            <Head title="My Tickets"/>

            {/*@ts-ignore*/}
            <DataTable columns={columns} url={route('tickets.dataTable')} />

        </AuthenticatedLayout>
    );
}

export default TicketsList;
