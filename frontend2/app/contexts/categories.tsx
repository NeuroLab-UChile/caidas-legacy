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
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchCategories = async () => {
    if (!isAuthenticated) {
      setCategories([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await apiService.categories.getAll();
      const apiData = response.data as Category[];
      setCategories(apiData);
    } catch (err) {
      console.error("Error fetching categories:", err);
      setError("Error al cargar las categorías");
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchCategories();
    } else {
      setCategories([]);
      setSelectedCategory(null);
    }
  }, [isAuthenticated]);

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
