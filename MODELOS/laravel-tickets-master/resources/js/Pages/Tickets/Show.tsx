import React, {FormEventHandler, useEffect, useState} from 'react';
import {PageProps, Ticket, Comment, User, Team, Category} from "@/types";
import {Head, Link} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import UserMiniCard from "@/Components/UserMiniCard";
import CommentCard from "@/Components/CommentCard";
import RichTextEditor from "@/Components/RichTextEditor";
import {Separator} from "@/Components/ui/separator";
import {useForm} from "@inertiajs/react";
import {Button} from "@/Components/ui/button";
import InputError from "@/Components/InputError";
import {FaArrowLeft, FaPlus, FaRotate} from "react-icons/fa6";
import {Badge} from "@/Components/ui/badge";
import { ticketStatusMapping, getBadgeVariant } from '@/lib/dt-columns/tickets';
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/Components/ui/dialog";
import {Label} from "@/Components/ui/label";
import MultiSelectFormField from "@/Components/ui/multiselect";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/Components/ui/select";


interface Props extends PageProps {
    ticket: Ticket;
    users: User[];
    teams: Team[],
    ticketStatuses: string[]
}

function Show({auth, ticket, users, teams, ticketStatuses}: Props) {

    console.log(ticket);

    const [comments, setComments] = useState<Comment[]>(ticket.comments);
    const [assignedUsers, setAssignedUsers] = useState<User[]>(ticket.assignedUsers);
    const [assignedTeams, setAssignedTeams] = useState<Team[]>(ticket.assignedTeams);
    const [ticketStatus, setTicketStatus] = useState(ticket.status);

    const [openUsersDialog, setOpenUsersDialog] = useState(false);
    const [openTeamsDialog, setOpenTeamsDialog] = useState(false);
    const [openTicketStatusDialog, setOpenTicketStatusDialog] = useState(false);

    /**
    * comments form data
    */
    const {data, setData, post, reset, errors, processing} =
        useForm({
            message: "",
            ticket_id: ticket.id,
            user_id: auth.user.id
        });

    /**
     * assign users form data
     */
    const {data: assignUserData, setData: assignUserSetData, put: assignUserPut, reset: assignUserReset, errors: assignUserErrors, processing: assignUserProcessing} =
            useForm({
                users: assignedUsers.map(user => user.id as string)
            });

    /**
     * assign teams data
     */
    const {data: assignTeamData, setData: assignTeamSetData, put: assignTeamPut, reset: assignTeamReset, errors: assignTeamErrors, processing: assignTeamProcessing} =
            useForm({
                teams: assignedTeams.map(team => team.id as string)
            });

    /**
     * update ticket status form data
     */
    const {data: ticketStatusData, setData: ticketStatusSetData, put: ticketStatusPut, reset: ticketStatusReset, errors: ticketStatusErrors, processing: ticketStatusProcessing} =
        useForm({
            status: ticket.status
        });

    /**
     * handle assign users submission
     * @param e
     */
    const assignUsers: FormEventHandler = (e) => {
        e.preventDefault();

        assignUserPut(route('tickets.assign-users', {ticket: ticket.id}), {
            onSuccess: (params) => {
                const ticket = params.props.ticket as unknown as Ticket;
                setAssignedUsers(ticket.assignedUsers);
                setOpenUsersDialog(false);
                setAssignedTeams(ticket.assignedTeams);
            }
        })
    }

    /**
     * handle assign teams submission
     * @param e
     */
    const assignTeams: FormEventHandler = (e) => {
        e.preventDefault();

        assignTeamPut(route('tickets.assign-teams', {ticket: ticket.id}), {
            onSuccess: (params) => {
                const ticket = params.props.ticket as unknown as Ticket;
                setAssignedTeams(ticket.assignedTeams);
                setOpenTeamsDialog(false);
            }
        })
    }

    /**
     * handle ticket update status submission
     * @param e
     */
    const updateStatus: FormEventHandler = (e) => {
        e.preventDefault();

        ticketStatusPut(route('tickets.update-status', {ticket: ticket.id}), {
            onSuccess: (params) => {
                const ticket = params.props.ticket as unknown as Ticket;
                setTicketStatus(ticket.status);
                setOpenTicketStatusDialog(false);
            }
        })
    }

    /**
     * handle add comment submission
     * @param e
     */
    const addComment: FormEventHandler = (e) => {
        e.preventDefault();

        post(route('comments.store'), {
            onSuccess: (params) => {
                const ticket = params.props.ticket as unknown as Ticket;
                setComments(ticket.comments);
                reset('message');
            },
            preserveScroll: true
        });
    }

    useEffect(() => {
        return () => {
            reset('message')
        }
    }, []);

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className={"font-semibold text-xl text-gray-800 leading-tight"}>Ticket Detail</h2>
                    <Link href={route('tickets.index')}>
                        <Button><FaArrowLeft className={"me-2"}/> Back</Button>
                    </Link>
                </div>
            }
        >
            <Head title={"Ticket Detail"}/>

            <div className={"flex flex-wrap"}>
                <div className={"w-full md:w-4/12 border rounded p-3"}>
                    <div className={"mb-3"}>Ticket# <span className={"text-muted-foreground"}>{ticket.ticket_number}</span></div>
                    <div className={"mb-3"}>
                        <div className={"mb-2"}>Created By:</div>
                        <UserMiniCard user={ticket.user}/>
                    </div>

                    <div className={"mb-3 flex gap-2 items-center"}>
                        Status: {/*@ts-ignore*/}
                        <Badge variant={getBadgeVariant(ticket.status)} className={"capitalize px-2 py-1"}>{ticketStatusMapping[ticket.status]}</Badge>
                        {auth.user.permissions.includes('update_tickets_status') && <Dialog open={openTicketStatusDialog} onOpenChange={setOpenTicketStatusDialog} >
                            <DialogTrigger asChild>
                                <Button variant={"default"} size={"sm"}>
                                    <FaRotate/>
                                </Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[425px]">
                                <form onSubmit={updateStatus}>
                                    <DialogHeader>
                                        <DialogTitle>Update ticket status</DialogTitle>
                                    </DialogHeader>
                                    <div className="grid gap-4 py-4">
                                        <Label htmlFor={"users"}>Choose a status</Label>
                                        <Select defaultValue={ticketStatus} onValueChange={(value) => {
                                            ticketStatusSetData('status', value)
                                        }}>
                                            <SelectTrigger>
                                                <SelectValue placeholder={"Choose a Category"}/>
                                            </SelectTrigger>
                                            <SelectContent>
                                                {ticketStatuses.map((status) => (
                                                    <SelectItem key={status}
                                                                value={status}>
                                                        {/*@ts-ignore*/}
                                                        {ticketStatusMapping[status]}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <InputError message={ticketStatusErrors.status} className="mt-2"/>
                                    <DialogFooter>
                                        <Button disabled={ticketStatusProcessing} type="submit">
                                            Save changes
                                        </Button>
                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>}
                    </div>

                    <div className={"mb-2"}>
                        <div>Category: <span className={"text-muted-foreground"}>{ticket.category.name}</span></div>
                    </div>

                    <div className={"mb-3"}>Created At: <span
                        className={"text-muted-foreground"}>{ticket.created_at}</span>
                    </div>

                    <div className={"mb-3"}>
                        <div className={"mb-2 flex items-center"}>
                            Assigned To Users: {auth.user.permissions.includes('assign_users_to_tickets') && <div className={"ps-2"}>
                                <Dialog open={openUsersDialog} onOpenChange={setOpenUsersDialog}>
                                    <DialogTrigger asChild>
                                        <Button variant={"default"} size={"sm"}>
                                            <FaPlus/>
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[425px]">
                                        <form onSubmit={assignUsers}>
                                            <DialogHeader>
                                                <DialogTitle>Assign users to Ticket</DialogTitle>
                                            </DialogHeader>
                                            <div className="grid gap-4 py-4">
                                                <Label htmlFor={"users"}>Choose users</Label>
                                                <MultiSelectFormField
                                                    options={users.map(user => ({
                                                        value: user.id as string,
                                                        label: user.name
                                                    }))}
                                                    placeholder={"Choose users"}
                                                    onValueChange={(value) => {
                                                        assignUserSetData('users', value)
                                                    }
                                                    }
                                                    defaultValue={assignUserData.users}
                                                />
                                            </div>
                                            <InputError message={assignUserErrors.users} className="mt-2"/>
                                            <DialogFooter>
                                                <Button disabled={assignUserProcessing} type="submit">Save
                                                    changes</Button>
                                            </DialogFooter>
                                        </form>
                                    </DialogContent>
                                </Dialog>

                            </div>}
                        </div>
                        <div className={"flex gap-2 flex-wrap items-center"}>
                            {assignedUsers.map(user => (
                                <UserMiniCard user={user} key={user.id}/>
                            ))}
                        </div>
                    </div>

                    <div className={""}>
                        <div className={"mb-2 flex items-center"}>
                            Assigned To Teams: {auth.user.permissions.includes('assign_teams_to_tickets') && <div className={"ps-2"}>
                            <Dialog open={openTeamsDialog} onOpenChange={setOpenTeamsDialog}>
                                <DialogTrigger asChild>
                                    <Button variant={"default"} size={"sm"}>
                                        <FaPlus/>
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="sm:max-w-[425px]">
                                    <form onSubmit={assignTeams}>
                                        <DialogHeader>
                                            <DialogTitle>Assign teams to Ticket</DialogTitle>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <Label htmlFor={"teams"}>Choose teams</Label>
                                            <MultiSelectFormField
                                                options={teams.map(team => ({
                                                    value: team.id as string,
                                                    label: team.name
                                                }))}
                                                placeholder={"Choose teams"}
                                                onValueChange={(value) => {
                                                    assignTeamSetData('teams', value)
                                                }
                                                }
                                                defaultValue={assignTeamData.teams}
                                            />
                                        </div>
                                        <InputError message={assignTeamErrors.teams} className="mt-2"/>
                                        <DialogFooter>
                                            <Button disabled={assignTeamProcessing} type="submit">
                                                Save changes
                                            </Button>
                                        </DialogFooter>
                                    </form>
                                </DialogContent>
                            </Dialog>

                        </div>}
                        </div>
                        <div className={"flex flex-wrap gap-2"}>
                            {assignedTeams.map(team => (
                                <div className={"py-2 px-3 border rounded"}>{team.name}</div>
                            ))}
                        </div>
                    </div>

                </div>
                <div className={"w-full md:w-8/12 border rounded p-3"}>
                    <h2 className={"text-xl"}>{ticket.title}</h2>
                    <p className={"text-muted-foreground mt-2"}
                       dangerouslySetInnerHTML={{__html: ticket.description}}/>

                    <div className={"comments mt-2"}>
                        {comments.map(comment => (
                            <CommentCard comment={comment} ticket={ticket} key={comment.id}/>
                        ))}
                    </div>

                    <Separator />

                    {(auth.user.permissions.includes('comment_on_tickets') && ticket.status !== 'closed') && <form onSubmit={addComment}>
                        <div className={"mt-2"}>
                            <RichTextEditor data={data.message} onChange={(event, editor) => {
                                setData('message', editor.getData())
                            }} id={"message"}/>
                            <InputError message={errors.message} className="mt-2"/>
                        </div>
                        <Button disabled={processing} className={"mt-2"}>Add Comment</Button>
                    </form>}
                </div>
            </div>

        </AuthenticatedLayout>
    );
}

export default Show;
