import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/apiService";
import { Category } from "../types/category";

interface CategoriesContextType {
  categories: Category[];
  selectedCategory: Category | null;
  setSelectedCategory: (category: Category | null) => void;
  loading: boolean;
  error: string | null;
}

const CategoriesContext = createContext<CategoriesContextType | undefined>(
  undefined
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

      console.log("Categorías cargadas:", apiData); // Debug log
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
    console.log("Estableciendo categoría seleccionada:", category); // Debug log
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

export function useCategories() {
  const context = useContext(CategoriesContext);
  if (context === undefined) {
    throw new Error("useCategories must be used within a CategoriesProvider");
  }
  return context;
}
