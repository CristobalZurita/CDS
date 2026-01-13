import React from 'react';
import {Ticket, Comment} from "@/types";
import {Avatar, AvatarFallback, AvatarImage} from "@/Components/ui/avatar";

interface Props {
    ticket: Ticket,
    comment: Comment
}

function CommentCard({ticket, comment}: Props) {
    return (
        <div className={"flex justify-between items-start mb-3 " + (comment.user_id !== ticket.user_id ? "flex-row-reverse" : "")}>
            <div className={"flex justify-between p-3 rounded border items-start w-9/12 " + (comment.user_id !== ticket.user_id ? "flex-row-reverse" : "")}>
                <Avatar className={"w-8 h-8 rounded-full " + (comment.user_id !== ticket.user_id ? "ms-3" : "me-3")}>
                    <AvatarImage src={comment.user.avatar} />
                    <AvatarFallback>LT</AvatarFallback>
                </Avatar>
                <div className={"w-full " + (comment.user_id !== ticket.user_id ? "text-right" : "")}>
                    <div>{comment.user.name}</div>
                    <div className={"text-muted-foreground text-justify"}
                         dangerouslySetInnerHTML={{__html: comment.message}}/>
                    <small className={"text-muted-foreground"}>{comment.created_at}</small>
                </div>
            </div>
        </div>
    );
}

export default CommentCard;
