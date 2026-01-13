import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps} from "@/types";
import React from "react";
import { Button } from "@/Components/ui/button";
import { FaPlus } from "react-icons/fa6";
import CategoriesDataTable from "@/Components/partials/CategoriesDataTable";

function Index({ auth }: PageProps) {

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">Categories</h2>
                        <Link href={route('categories.create')}>
                            <Button><FaPlus className={"me-2"}/> Create</Button>
                        </Link>
                </div>
            }
        >
            <Head title="Categories"/>

            {/*@ts-ignore*/}
            <CategoriesDataTable url={route('categories.dataTable')} />

        </AuthenticatedLayout>
    );
}

export default Index;
