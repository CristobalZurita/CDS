import React, { FormEventHandler, useEffect } from 'react';
import {Head, Link, useForm, usePage} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {Category, PageProps, User} from "@/types";
import {Label} from "@/Components/ui/label";
import {Input} from "@/Components/ui/input";
import InputError from "@/Components/InputError";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/Components/ui/select";
import {Button} from "@/Components/ui/button";
import {FaArrowLeft} from "react-icons/fa6";

interface Props extends PageProps {
    user?: User,
    roles: string[]
}
function CreateEdit({auth, user, roles}: Props) {

    const {data, setData, post, put, processing, errors, reset} = useForm({
        id: user?.id ?? '',
        name: user?.name ?? '',
        role: user?.role ?? '',
        email: user?.email ?? '',
        password: ''
    });

    const createUser: FormEventHandler = (e) => {
        e.preventDefault();

        if (data.id) {
            put(route('users.update', {user: data.id}), {
                onSuccess: (params) => {
                    reset('email', 'name', 'password', 'role');
                }
            })
        } else {
            post(route('users.store'), {
                onSuccess: (params) => {
                    reset('email', 'name', 'password', 'role');
                }
            })
        }
    }

    useEffect(() => {
        return () => {
            reset('email', 'name', 'password', 'role');
        }
    }, []);

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={<div className={"flex justify-between"}>
                <h2 className="font-semibold text-xl text-gray-800 leading-tight">
                    {user ? "Update" : "Create"} User
                </h2>
                <Link href={route('users.index')}>
                    <Button><FaArrowLeft className={"me-2"}/> Back</Button>
                </Link>
            </div>}
        >
            <Head title={user ? "Update" : "Create" + " User"} />

            <form onSubmit={createUser}>
                <div className={"flex justify-between flex-wrap"}>
                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="name">Name</Label>
                        <Input
                            id="name"
                            type="text"
                            name="name"
                            value={data.name}
                            className="mt-1 block w-full"
                            autoComplete="name"
                            autoFocus={true}
                            onChange={(e) => setData('name', e.target.value)}
                        />

                        <InputError message={errors.name} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            type="email"
                            name="email"
                            value={data.email}
                            className="mt-1 block w-full"
                            autoComplete="email"
                            onChange={(e) => setData('email', e.target.value)}
                        />

                        <InputError message={errors.email} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="password">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            name="password"
                            value={data.password}
                            className="mt-1 block w-full"
                            autoComplete="password"
                            onChange={(e) => setData('password', e.target.value)}
                        />

                        <InputError message={errors.password} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="role" className={"block mb-3"}>Role</Label>
                        <div>
                            <Select defaultValue={data.role} onValueChange={(value) => {
                                setData('role', value)
                            }}>
                                <SelectTrigger>
                                    <SelectValue placeholder={"Choose a role for user"}/>
                                </SelectTrigger>
                                <SelectContent>
                                    {roles.map((role) => (
                                        <SelectItem key={role}
                                                    value={role}>{<span
                                            className={"capitalize"}>{role.replaceAll('_', ' ')}</span>}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <InputError message={errors.role} className="mt-2"/>
                        </div>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Button disabled={processing}>{user ? "Update" : "Create"} User</Button>
                    </div>
                </div>
            </form>

        </AuthenticatedLayout>
);
}

export default CreateEdit;
