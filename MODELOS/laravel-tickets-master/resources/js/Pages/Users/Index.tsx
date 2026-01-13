import React from 'react';
import {PageProps} from "@/types";
import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {Button} from "@/Components/ui/button";
import {FaPlus} from "react-icons/fa6";
import UsersDataTable from "@/Components/partials/UsersDataTable";
interface Props extends PageProps{

}

function Index({auth}: Props) {

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">Users</h2>

                    {auth.user.permissions.includes('create_users') && <Link href={route('users.create')}>
                        <Button size={"sm"}>
                            <FaPlus className={"me-2"} />
                            <span>Create</span>
                        </Button>
                    </Link>}
                </div>
            }
        >
            <Head title={"Users"} />
            <UsersDataTable />
        </AuthenticatedLayout>
    );
}

export default Index;
