import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/apiService";
import { Category } from "../types/category";
import { useAuth } from "./auth";

interface CategoriesContextType<T = Category> {
  categories: T[];
  selectedCategory: T | null;
  setSelectedCategory: (category: T | null) => void;
  loading: boolean;
  error: string | null;
  fetchCategories: () => Promise<void>;
}

export const CategoriesContext = createContext<CategoriesContextType>(
  {} as CategoriesContextType
);

export function CategoriesProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchCategories();
    }
  }, [isAuthenticated]);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await apiService.categories.getAll();
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
      setError("Error al cargar las categorías");
    } finally {
      setLoading(false);
    }
  };

  const handleSetSelectedCategory = (category: Category | null) => {
    setSelectedCategory(category);
  };

  return (
    <CategoriesContext.Provider
      value={{
        categories,
        selectedCategory,
        setSelectedCategory: handleSetSelectedCategory,
        loading,
        error,
        fetchCategories,
      }}
    >
      {children}
    </CategoriesContext.Provider>
  );
}

export const useCategories = () => useContext(CategoriesContext);
