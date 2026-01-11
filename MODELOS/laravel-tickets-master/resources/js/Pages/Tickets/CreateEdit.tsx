import React, {FormEventHandler, useEffect} from 'react';
import {Category, PageProps, Ticket, User} from "@/types";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {Link, Head, useForm} from "@inertiajs/react";
import {Button} from "@/Components/ui/button";
import {FaArrowLeft} from "react-icons/fa6";
import {Label} from "@/Components/ui/label";
import {Input} from "@/Components/ui/input";
import InputError from "@/Components/InputError";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/Components/ui/select";
import RichTextEditor from "@/Components/RichTextEditor";

interface Props extends PageProps {
    ticket?: Ticket;
    categories: Category[]
}

function CreateEdit({auth, ticket, categories}: Props) {

    const {data, setData, post, put, processing, errors, reset} = useForm({
        id: ticket?.id ?? '',
        title: ticket?.title ?? '',
        description: ticket?.description ?? '',
        category_id: ticket?.category_id ?? '',
        user_id: auth.user.id
    });

    const submit: FormEventHandler = (e) => {
        e.preventDefault();

        if (ticket) {
            put(route('tickets.update', {ticket: ticket.id}));
        } else {
            post(route('tickets.store'));
        }
    }

    useEffect(() => {
        return () => {
            reset('title', 'description', 'category_id')
        }
    }, []);

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">Create Ticket</h2>
                    <Link href={route('tickets.index')}>
                        <Button><FaArrowLeft className={"me-2"}/> Back</Button>
                    </Link>
                </div>
            }
        >
            <Head title={"Create Ticket"} />

            <form onSubmit={submit}>
                <div className={"flex justify-between flex-wrap"}>
                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="name">Title</Label>

                        <Input
                            id="name"
                            type="name"
                            name="name"
                            value={data.title}
                            className="mt-1 block w-full"
                            autoComplete="title"
                            // isFocused={true}
                            onChange={(e) => setData('title', e.target.value)}
                        />

                        <InputError message={errors.title} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="category_id" className={"block mb-3"}>Choose a Category</Label>
                        <div>
                            <Select defaultValue={"" + data.category_id} onValueChange={(value) => {
                                setData('category_id', value)
                            }}>
                                <SelectTrigger>
                                    <SelectValue placeholder={"Choose a Category"}/>
                                </SelectTrigger>
                                <SelectContent>
                                    {categories.map((category: Category) => (
                                        <SelectItem key={category.id}
                                                    value={"" + category.id}>{category.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <InputError message={errors.category_id} className="mt-2"/>
                        </div>
                    </div>

                    <div className={"w-full p-3 flex-shrink-0"}>
                        <Label htmlFor="description" className={"block mb-3"}>Add a Description</Label>
                        <RichTextEditor data={data.description} onChange={(event, editor) => {
                            setData('description', editor.getData())
                        }} id={"description"}/>
                        <InputError message={errors.description} className="mt-2"/>
                    </div>

                    <div className={"w-full p-3"}>
                        <Button disabled={processing} type={"submit"}>{ticket ? "Update" : "Create"} Ticket</Button>
                    </div>
                </div>
            </form>

        </AuthenticatedLayout>
);
}

export default CreateEdit;
