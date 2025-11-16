"use client";

import React, { useState, useEffect } from 'react';

interface IdealPrompt {
  id: string;
  title: string;
  prompt: string;
  description: string;
  category: string;
  icon: string;
}

interface IdealPromptButtonsProps {
  onPromptClick: (prompt: string) => void;
}

export default function IdealPromptButtons({ onPromptClick }: IdealPromptButtonsProps) {
  const [prompts, setPrompts] = useState<IdealPrompt[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIdealPrompts();
  }, []);

  const fetchIdealPrompts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/ideal-prompts');
      const data = await response.json();
      setPrompts(data.prompts || []);
    } catch (error) {
      console.error('Error fetching ideal prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="min-w-[280px] h-20 bg-gray-100 rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-3 mb-4 overflow-x-auto pb-2 scrollbar-hide">
      {prompts.map((prompt) => (
        <button
          key={prompt.id}
          onClick={() => onPromptClick(prompt.prompt)}
          className="min-w-[280px] flex-shrink-0 bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200 rounded-lg p-4 text-left transition-all duration-200 hover:shadow-md hover:scale-[1.02] active:scale-[0.98]"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">{prompt.icon}</span>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-gray-900 text-sm mb-1 truncate">
                {prompt.title}
              </h3>
              <p className="text-xs text-gray-600 line-clamp-2">
                {prompt.description}
              </p>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
