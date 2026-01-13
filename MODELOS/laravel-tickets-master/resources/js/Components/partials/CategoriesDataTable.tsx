import DataTable, {dataTableRef} from "@/Components/DataTable";
import React, {useRef} from "react";
import axios from "axios";
import useColumns from "@/lib/dt-columns/categories";


function CategoriesDataTable({url = route('categories.dataTable')}) {

    const dataTableRef = useRef<dataTableRef>(null);

    const handleDeleteCategory = (id: number) => {

        if (confirm("Are you sure to delete?")) {
            axios.delete(route('categories.destroy', {id}))
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
        deleteCategoryCallback: handleDeleteCategory
    });

    return (
        <>
            {/*@ts-ignore*/}
            <DataTable columns={columns} url={url} ref={dataTableRef} />
        </>
    );
}

export default CategoriesDataTable;
