import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/apiService";
import { Category } from "../types/category";

interface CategoriesContextType<T = Category> {
  categories: T[];
  selectedCategory: T | null;
  setSelectedCategory: (category: T | null) => void;
  loading: boolean;
  error: string | null;
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

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await apiService.categories.getAll();
      const apiData = response.data as Category[];

      setCategories(apiData);
    } catch (err) {
      console.error("Error fetching categories:", err);
      setError("Error al cargar las categorías");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

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
      }}
    >
      {children}
    </CategoriesContext.Provider>
  );
}

export const useCategories = () => useContext(CategoriesContext);
