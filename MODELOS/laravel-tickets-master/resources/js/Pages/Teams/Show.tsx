import React from 'react';
import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps, Team} from "@/types";
import UsersDataTable from "@/Components/partials/UsersDataTable";
import CategoriesDataTable from "@/Components/partials/CategoriesDataTable";
import {Button} from "@/Components/ui/button";
import {FaArrowLeft} from "react-icons/fa6";
import {FaEdit} from "react-icons/fa";

interface Props extends PageProps {
    team: Team
}

function Show({auth, team}: Props) {

    const usersDataTableUrl = route('users.dataTable') + `?team=${team.id}`;
    const categoriesDataTableUrl = route('categories.dataTable') + `?team=${team.id}`;

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={<div className={"flex justify-between"}>
                <h2 className="font-semibold text-xl text-gray-800 leading-tight">
                    Team Information
                </h2>

                <div>
                    <Link href={auth.user.role !== 'admin' ? route('dashboard') : route('teams.index')}>
                        <Button size={"sm"}>
                            <FaArrowLeft/>
                        </Button>
                    </Link>

                    {auth.user.permissions.includes('update_teams') &&
                        <Link href={route('teams.edit', {team: team.id})}>
                            <Button className={"ms-2"} size={"sm"}>
                                <FaEdit/>
                            </Button>
                        </Link>
                    }
                </div>
            </div>}
        >
            <Head title={team.name}/>
            <div className={"p-3"}>
                <h2 className={"text-3xl mb-2"}>{team.name}</h2>
                <p className={"text-muted-foreground"} dangerouslySetInnerHTML={{__html: team.description}}/>

                <h3 className={"text-xl mt-2"}>Team Manager</h3>
                <p className={"text-muted-foreground"}>{team.manager.name}:
                    <a className={"text-primary ms-2"} href={"mailto:" + team.manager.email}>{team.manager.email}</a>
                </p>
            </div>

            <h3 className={"px-3 text-xl"}>Team Members</h3>
            <UsersDataTable url={usersDataTableUrl}></UsersDataTable>

            <h3 className={"px-3 text-xl"}>Team Categories</h3>
            <CategoriesDataTable url={categoriesDataTableUrl}></CategoriesDataTable>

        </AuthenticatedLayout>
    );
}

export default Show;
