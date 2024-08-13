// frontend/src/types/index.ts

export type Result = {
    text: string;
    metadata: {
      source: string;
      page: number;
    };
    image: string;
    distance: number;
  };
  