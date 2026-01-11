import React, {ReactNode} from 'react';
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from "@/Components/ui/card";
import {FaArrowRight} from "react-icons/fa6";
import {Link} from "@inertiajs/react";

interface Props {
    title: string;
    count: number;
    url?: string;
    icon?: ReactNode;
    color?: string;
}

function DashboardCard({title, count, url, icon, color = "text-primary"}: Props) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className={"flex justify-between " + color}>
                    {icon}
                    <div className="text-5xl w-3/4 text-center">{count}</div>
                </div>
            </CardContent>
            <CardFooter>
                <p className="text-sm">
                    {url && <Link href={url} className="inline-flex items-center font-semibold text-indigo-700 dark:text-indigo-300">
                        View detail
                        <FaArrowRight className={"ms-2"}/>
                    </Link>}
                </p>
            </CardFooter>
        </Card>
    );
}

export default DashboardCard;
