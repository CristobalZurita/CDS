import React from 'react';
import {User} from "@/types";

interface Props {
    user: User;
}

function UserMiniCard({user}: Props) {
    return (
        <div className={"inline-flex border rounded py-2 px-3 justify-between items-center"}>
            <img src={user.avatar} alt={user.name}
                 className={"w-8 rounded-full"}/>

            <span className={"ms-3 text-muted-foreground"}>{user.name}</span>
        </div>
    );
}

export default UserMiniCard;
