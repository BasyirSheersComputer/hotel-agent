
"use client";

import React, { useEffect, useState } from 'react';
import { useAuth, useAuthHeaders } from '@/contexts/AuthContext';
import { Building2 } from 'lucide-react';


interface Property {
    property_id: string;
    name: string;
    slug: string;
}

export function PropertySwitcher() {
    const { user, switchProperty } = useAuth();
    const headers = useAuthHeaders();
    const [properties, setProperties] = useState<Property[]>([]);

    // Fetch properties on mount
    useEffect(() => {
        const fetchProperties = async () => {
            if (!user?.org_id) return;
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                // Only try to fetch if we have a token (user logged in)
                if (!headers.Authorization) return;

                const res = await fetch(`${API_URL}/api/properties`, { headers: headers as HeadersInit });

                if (res.ok) {
                    setProperties(await res.json());
                } else {
                    console.log("Failed to fetch properties, using fallback for demo if needed");
                }
            } catch (error) {
                console.error("Failed to fetch properties", error);
            }
        };

        fetchProperties();
    }, [user, headers.Authorization]);

    const handleCreateProperty = async () => {
        const name = window.prompt("Enter new property name:");
        if (!name) return;

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/api/properties`, {
                method: "POST",
                headers: {
                    ...(headers as Record<string, string>),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name })
            });

            if (res.ok) {
                const newProp = await res.json();
                setProperties([...properties, newProp]);
                switchProperty(newProp.property_id);
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail}`);
            }
        } catch (e) {
            console.error(e);
            alert("Failed to create property");
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const val = e.target.value;
        if (val === "create_new") {
            handleCreateProperty();
        } else {
            switchProperty(val);
        }
    };

    return (
        <div className="flex items-center space-x-2 w-full">
            <Building2 className="w-4 h-4 text-slate-400" />
            <select
                value={user?.property_id || "all"}
                onChange={handleChange}
                className="bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5"
            >
                <option value="all">All Properties</option>
                {properties.map((property) => (
                    <option key={property.property_id} value={property.property_id}>
                        {property.name}
                    </option>
                ))}
                <option disabled>──────────</option>
                <option value="create_new"> + Create New Property</option>
            </select>
        </div>
    );
}
