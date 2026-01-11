import React, { FormEventHandler, useEffect } from 'react';
import {Head, Link, useForm, usePage} from "@inertiajs/react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import {PageProps, Category} from "@/types";
import { FaArrowLeft } from "react-icons/fa6";

import InputError from '@/Components/InputError';

import {Input} from '@/Components/ui/input';
import {Label} from '@/Components/ui/label';
import {Button} from '@/Components/ui/button';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/Components/ui/select';
import RichTextEditor from "@/Components/RichTextEditor";

interface Props extends PageProps {
    categories: Category[],
    category?: Category
}

function CreateEdit({auth, category, categories}: Props) {

    const {data, setData, post, put, processing, errors, reset} = useForm({
        id: category?.id ?? '',
        name: category?.name ?? '',
        description: category?.description ?? '',
        category_id: category?.category_id ?? '',
    });

    useEffect(() => {
        return () => {
            reset('category_id', 'description', 'name')
        }
    }, []);

    const submit: FormEventHandler = (e) => {
        e.preventDefault()

        if (data.id) {
            put(route('categories.update', {id: data.id}))
        } else {
            post(route('categories.store'))
        }
    }

    return (
        <AuthenticatedLayout
            user={auth.user}
            header={
                <div className={"flex justify-between"}>
                    <h2 className="font-semibold text-xl text-gray-800 leading-tight">{category ? "Update" : "Create"} Category</h2>
                    <Link href={route('categories.index')}>
                        <Button><FaArrowLeft className={"me-2"}/> Back</Button>
                    </Link>
                </div>
            }
        >
            <Head title={"Create Category"}/>

            <form onSubmit={submit}>
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
                            // isFocused={true}
                            onChange={(e) => setData('name', e.target.value)}
                        />

                        <InputError message={errors.name} className="mt-2"/>
                    </div>

                    <div className={"w-full md:w-1/2 p-3 flex-shrink-0"}>
                        <Label htmlFor="category_id" className={"block mb-3"}>Category</Label>
                        <div>
                            <Select defaultValue={"" + data.category_id} onValueChange={(value) => {setData('category_id', value)}}>
                                <SelectTrigger>
                                    <SelectValue placeholder={"Select parent category"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {categories.map((category: Category) => (
                                        <SelectItem key={category.id} value={"" + category.id}>{category.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <InputError message={errors.category_id} className="mt-2"/>
                        </div>
                    </div>

                    <div className={"p-3 w-full flex-shrink-0"}>
                        <Label htmlFor="description" className={"mb-3 block"}>Add a description</Label>
                        <RichTextEditor data={data.description} onChange={(event, editor) => {
                            setData('description', editor.getData())
                        }} id={"description"} />
                        <InputError message={errors.description} className="mt-2"/>
                    </div>

                    <div className={"p-3 w-full flex-shrink-0"}>
                        <Button type={"submit"}>{category ? "Update" : "Create"}</Button>
                    </div>
                </div>
            </form>

        </AuthenticatedLayout>
    );
}

export default CreateEdit;
