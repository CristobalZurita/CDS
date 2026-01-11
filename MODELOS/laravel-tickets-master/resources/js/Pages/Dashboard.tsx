import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head } from '@inertiajs/react';
import { PageProps } from '@/types';
import React from "react";
import {
    FaFileContract,
    FaFileLines,
    FaSitemap,
    FaUserGear,
    FaUsersBetweenLines,
    FaUserShield, FaUserTag,
    FaUserTie
} from "react-icons/fa6";
import DashboardCard from "@/Components/DashboardCard";

interface Props extends PageProps {
    stats: {
        [key: string] : {} | any
    }
}

export default function Dashboard({ auth, stats }: Props) {

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={<h2 className="font-semibold text-xl text-gray-800 leading-tight">Dashboard</h2>}
        >
            <Head title="Dashboard" />

            <div className="py-4">
                <div className="max-w-7xl mx-auto sm:px-2 lg:px-4">
                    <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                        <div className="bg-gray-200 dark:bg-gray-800 bg-opacity-25 grid grid-cols-1 md:grid-cols-4 gap-6 lg:gap-6 p-2 lg:p-4">


                            <DashboardCard
                                title={"Total Tickets"}
                                count={stats.tickets.total}
                                color={"text-primary"}
                                icon={<FaFileLines className={"w-12 h-12"} />}
                                url={route('tickets.index')}
                            />

                            <DashboardCard
                                title={"Open Tickets"}
                                count={stats.tickets.open}
                                color={"text-info"}
                                icon={<FaFileLines className={"w-12 h-12"} />}
                                url={route('tickets.index')}
                            />


                            {auth.user.role !== 'admin' &&
                                <DashboardCard
                                    title={"Resolved Tickets"}
                                    count={stats.tickets.resolved}
                                    color={"text-success"}
                                    icon={<FaFileContract className={"w-12 h-12"} />}
                                    url={route('tickets.index')}
                                />
                            }

                            {auth.user.role === 'admin' && <>
                                <DashboardCard
                                    title={"Categories"}
                                    count={stats.categories}
                                    color={"text-warning"}
                                    icon={<FaSitemap  className={"w-12 h-12"} />}
                                    url={route('categories.index')}
                                />

                                <DashboardCard
                                    title={"Teams"}
                                    count={stats.teams}
                                    color={"text-success"}
                                    icon={<FaUsersBetweenLines className={"w-12 h-12"} />}
                                    url={route('teams.index')}
                                />

                                <DashboardCard
                                    title={"Managers"}
                                    count={stats.users.managers}
                                    color={"text-info"}
                                    icon={<FaUserTie className={"w-12 h-12"} />}
                                    url={route('users.index')}
                                />

                                <DashboardCard
                                    title={"Team Leads"}
                                    count={stats.users.team_leads}
                                    color={"text-primary"}
                                    icon={<FaUserShield className={"w-12 h-12"} />}
                                    url={route('users.index')}
                                />

                                <DashboardCard
                                    title={"Team Members"}
                                    count={stats.users.team_members}
                                    color={"text-warning"}
                                    icon={<FaUserGear className={"w-12 h-12"} />}
                                    url={route('teams.index')}
                                />

                                <DashboardCard
                                    title={"Customers"}
                                    count={stats.users.customers}
                                    color={"text-info"}
                                    icon={<FaUserTag className={"w-12 h-12"} />}
                                    url={route('teams.index')}
                                />

                            </>}

                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
