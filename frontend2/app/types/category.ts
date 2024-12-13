export interface Category {
  id: number;
  name: string;
  icon: string; // Este será el string en base64
  root_node: {
    type: string;
    description: string;
    // ... otros campos del nodo
  };
  form?: any;
  form_response?: any;
  result_text?: string | null;
  result_color?: string | null;
} 