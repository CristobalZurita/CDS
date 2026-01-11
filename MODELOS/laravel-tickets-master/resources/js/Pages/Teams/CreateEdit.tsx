import React, {FormEventHandler, useEffect, useState} from 'react';
import {Head, Link, useForm} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps, Category, User, Team} from "@/types";
import { FaArrowLeft } from "react-icons/fa6";

import InputError from '@/Components/InputError';

import {Input} from '@/Components/ui/input';
import {Label} from '@/Components/ui/label';
import {Button} from '@/Components/ui/button';

import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/Components/ui/select";
import MultiSelectFormField from "@/Components/ui/multiselect";
import RichTextEditor from "@/Components/RichTextEditor";

interface Props extends PageProps {
    managers: User[],
    users: User[],
    team: Team,
    categories: Category[]
}

function CreateEdit({ auth, managers, users, team, categories }: Props) {

    const [teamUsers, setTeamUsers] =
        useState<string[]>(team && team.users ? team.users.map(user => (user.id as string)) : []);
    const [teamCategories, setTeamCategories] =
        useState<string[]>(team && team.categories ? team.categories.map(category => (category.id as string)): []);

    const {data, setData, post, put, processing, errors, reset} = useForm({
        id: team?.id ?? '',
        name: team?.name ?? '',
        description: team?.description ?? '',
        manager_id: team?.manager_id ?? '',
        users: teamUsers,
        categories: teamCategories
    });

    useEffect(() => {
        return () => {
            setTeamUsers([]);
            reset('manager_id', 'description', 'name', 'users')
        }
    }, []);

    useEffect(() => {
        setData('users', teamUsers)
    }, [teamUsers]);

    useEffect(() => {
        setData('categories', teamCategories)
    }, [teamCategories]);

    const submit: FormEventHandler = (e) => {
        e.preventDefault()

        if (data.id) {
            put(route('teams.update', {id: data.id}))
        } else {
            post(route('teams.store'))
        }
    }

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">{team ? "Update" : "Create"} Team</h2>
                    <Link href={route('teams.index')}>
                        <Button><FaArrowLeft className={"me-2"}/> Back</Button>
                    </Link>
                </div>
            }
        >
            <Head title={team ? "Update" : "Create" + " Team"}/>

            <form onSubmit={submit}>
                <div className={"flex justify-between flex-wrap"}>
                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="name">Name</Label>

                        <Input
                            id="name"
                            type="name"
                            name="name"
                            value={data.name}
                            className="mt-1 block w-full"
                            autoComplete="name"
                            // isFocused={true}
                            onChange={(e) => setData('name', e.target.value)}
                        />

                        <InputError message={errors.name} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="category_id" className={"block mb-3"}>Choose a Manager</Label>
                        <div>
                            <Select defaultValue={"" + data.manager_id} onValueChange={(value) => {
                                setData('manager_id', value)
                            }}>
                                <SelectTrigger>
                                    <SelectValue placeholder={"Choose a Manager"}/>
                                </SelectTrigger>
                                <SelectContent>
                                    {managers.map((manager: User) => (
                                        <SelectItem key={manager.id}
                                                    value={"" + manager.id}>{manager.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <InputError message={errors.manager_id} className="mt-2"/>
                        </div>
                    </div>


                    <div className={"p-3 w-full flex-shrink-0"}>
                        <Label htmlFor="description" className={"mb-3 block"}>Add a description</Label>
                        <RichTextEditor data={data.description} onChange={(event, editor) => {
                            setData('description', editor.getData())
                        }} id={"description"} />
                        <InputError message={errors.description} className="mt-2"/>
                    </div>

                    {auth.user.permissions.includes('add_users_to_teams') && <div className={"p-3 w-full md:w-1/2"}>
                        <Label htmlFor="members" className={"mb-3 block"}>Choose Team Members (optional)</Label>
                        <MultiSelectFormField
                            options={users.map((user) => ({value: user.id as string, label: user.name}))}
                            placeholder={"Choose Team Members"}
                            defaultValue={teamUsers}
                            onValueChange={setTeamUsers}/>
                    </div>}

                    {auth.user.permissions.includes('add_categories_to_teams') && <div className={"p-3 w-full md:w-1/2"}>
                        <Label htmlFor="categories" className={"mb-3 block"}>Choose Categories (optional)</Label>
                        <MultiSelectFormField
                            options={categories.map((category) => ({
                                value: category.id as string,
                                label: category.name
                            }))}
                            placeholder={"Choose Categories"}
                            defaultValue={teamCategories}
                            onValueChange={setTeamCategories} />
                    </div>}

                    <div className={"p-3 w-full flex-shrink-0"}>
                        <Button disabled={processing} type={"submit"}>{team ? "Update" : "Create"}</Button>
                    </div>

                </div>
            </form>

        </AuthenticatedLayout>
    );
}

export default CreateEdit;
