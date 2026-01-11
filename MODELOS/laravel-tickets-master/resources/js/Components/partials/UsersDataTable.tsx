import React, {useRef} from 'react';
import DataTable, {dataTableRef} from "@/Components/DataTable";
import useColumns from "@/lib/dt-columns/users";
import axios from "axios";

function UsersDataTable({url = route('users.dataTable')}) {

    const dataTableRef = useRef<dataTableRef>(null);

    const handleDeleteUser = (id: number) => {

        if (confirm("Are you sure to delete?")) {
            axios.delete(route('users.destroy', {user: id}))
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
        deleteUserCallback: handleDeleteUser
    });

    return (
        <>
            {/*@ts-ignore*/}
            <DataTable columns={columns} url={url} />
        </>
    );
}

export default UsersDataTable;
