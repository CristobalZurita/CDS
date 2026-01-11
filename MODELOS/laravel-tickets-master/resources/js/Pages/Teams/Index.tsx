import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps} from "@/types";
import DataTable, {dataTableRef} from "@/Components/DataTable";
import React, {useRef} from "react";
import useColumns from "@/lib/dt-columns/teams";
import { Button } from "@/Components/ui/button";
import { FaPlus } from "react-icons/fa6";
import axios from "axios";


function Index({ auth }: PageProps) {

    const dataTableRef = useRef<dataTableRef>(null);

    const handleDeleteTeam = (id: number) => {

        if (confirm("Are you sure to delete?")) {
            axios.delete(route('teams.destroy', {id}))
                .then(response => {
                    if (dataTableRef.current) {
                        dataTableRef.current.refreshData()
                    }
                }).catch(error => {
                console.error(error)
            })
        }
    }

    const columns = useColumns({
        deleteTeamCallback: handleDeleteTeam
    });

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">Teams</h2>

                    {auth.user.permissions.includes('create_teams') && <Link href={route('teams.create')}>
                        <Button><FaPlus className={"me-2"}/> Create</Button>
                    </Link>}
                </div>
            }
        >
            <Head title={"Teams"} />

            {/*@ts-ignore*/}
            <DataTable columns={columns} url={route('teams.dataTable')} ref={dataTableRef} />

        </AuthenticatedLayout>
    );
}

export default Index;
