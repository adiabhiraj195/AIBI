import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select";
import { Plus } from 'lucide-react';

interface DashboardPinModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (title: string, category: string) => Promise<void>;
    initialTitle?: string;
}

const CATEGORIES = [
    "General",
    "Revenue",
    "Forecasting",
    "Operational",
    "Strategic",
    "Risks"
];

export function DashboardPinModal({ isOpen, onClose, onConfirm, initialTitle = "" }: DashboardPinModalProps) {
    const [title, setTitle] = useState(initialTitle);
    const [category, setCategory] = useState("General");
    const [isCustomCategory, setIsCustomCategory] = useState(false);
    const [customCategory, setCustomCategory] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Update title when prop changes
    React.useEffect(() => {
        setTitle(initialTitle);
    }, [initialTitle]);

    const handleConfirm = async () => {
        if (!title.trim()) return;

        setIsSubmitting(true);
        const finalCategory = isCustomCategory ? (customCategory.trim() || "General") : category;

        try {
            await onConfirm(title, finalCategory);
            onClose();
        } catch (error) {
            console.error("Failed to pin", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px] bg-[#0f1629] border-gray-800 text-white">
                <DialogHeader>
                    <DialogTitle>Pin to Dashboard</DialogTitle>
                    <DialogDescription className="text-gray-400">
                        Save this visualization to your personal dashboard.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                        <Label htmlFor="title" className="text-gray-300">Title</Label>
                        <Input
                            id="title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="bg-gray-900 border-gray-700 text-white focus:border-emerald-500"
                            placeholder="e.g. Q3 Revenue Forecast"
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="category" className="text-gray-300">Category</Label>
                        {!isCustomCategory ? (
                            <div className="flex gap-2">
                                <Select value={category} onValueChange={setCategory}>
                                    <SelectTrigger className="bg-gray-900 border-gray-700 text-white focus:border-emerald-500 w-full">
                                        <SelectValue placeholder="Select category" />
                                    </SelectTrigger>
                                    <SelectContent className="bg-gray-900 border-gray-700 text-white">
                                        {CATEGORIES.map((cat) => (
                                            <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={() => setIsCustomCategory(true)}
                                    className="bg-gray-900 border-gray-700 hover:bg-gray-800 text-gray-300"
                                    title="Create new category"
                                >
                                    <Plus className="w-4 h-4" />
                                </Button>
                            </div>
                        ) : (
                            <div className="flex gap-2">
                                <Input
                                    id="custom-category"
                                    value={customCategory}
                                    onChange={(e) => setCustomCategory(e.target.value)}
                                    className="bg-gray-900 border-gray-700 text-white focus:border-emerald-500"
                                    placeholder="Enter new category name"
                                    autoFocus
                                />
                                <Button
                                    variant="ghost"
                                    onClick={() => setIsCustomCategory(false)}
                                    className="text-gray-400 hover:text-white"
                                >
                                    Cancel
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={onClose} className="bg-transparent border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleConfirm}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white"
                        disabled={isSubmitting || !title.trim()}
                    >
                        {isSubmitting ? "Pinning..." : "Pin to Dashboard"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
