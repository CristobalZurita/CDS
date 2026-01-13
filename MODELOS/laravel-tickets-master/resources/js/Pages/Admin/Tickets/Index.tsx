import React from 'react';
import TicketsList from "@/Components/partials/TicketsList";
import {PageProps} from "@/types";

function Index({ auth }: PageProps) {
    return (
        <TicketsList auth={auth} />
    );
}

export default Index;
