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

export const CategoriesProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
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

      // Si hay una categoría seleccionada, actualizar sus datos
      if (selectedCategory) {
        const updatedCategory = response.data.find(
          (c) => c.id === selectedCategory.id
        );
        if (
          updatedCategory &&
          JSON.stringify(updatedCategory) !== JSON.stringify(selectedCategory)
        ) {
          setSelectedCategory(updatedCategory);
        }
      }

      // Retornar los datos actualizados para uso externo
      return {
        categories: response.data,
        updatedSelectedCategory: selectedCategory
          ? response.data.find((c) => c.id === selectedCategory.id)
          : null,
      };
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
        fetchCategories: fetchCategories as () => Promise<void>,
      }}
    >
      {children}
    </CategoriesContext.Provider>
  );
};

export const useCategories = () => {
  const context = useContext(CategoriesContext);
  if (!context) {
    throw new Error("useCategories must be used within a CategoriesProvider");
  }
  return context;
};

export default CategoriesProvider;
