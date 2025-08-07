import React from 'react';
import { FiCheck } from 'react-icons/fi';

const RadioGroup = ({ 
  name, 
  value, 
  onChange, 
  options, 
  label, 
  required = false,
  disabled = false 
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-slate-700 font-medium mb-3 text-sm sm:text-base">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={`relative cursor-pointer group transition-all duration-200 ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={onChange}
              disabled={disabled}
              className="sr-only"
            />
            <div
              className={`relative p-4 rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-24 flex flex-col justify-center ${
                value === option.value
                  ? 'border-emerald-500 bg-emerald-50 shadow-lg shadow-emerald-100'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
              } ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {/* Selection indicator */}
              {value === option.value && (
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                  <FiCheck className="text-white text-sm font-bold" />
                </div>
              )}
              
              {/* Content */}
              <div className="flex items-center gap-3">
                {/* Icon */}
                {option.icon && (
                  <div className={`p-2 rounded-xl transition-colors duration-200 flex-shrink-0 ${
                    value === option.value 
                      ? 'bg-emerald-100 text-emerald-600' 
                      : 'bg-slate-100 text-slate-600'
                  }`}>
                    <option.icon className="text-lg" />
                  </div>
                )}
                
                {/* Text content */}
                <div className="flex-1 min-w-0">
                  <div className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${
                    value === option.value ? 'text-emerald-800' : 'text-slate-800'
                  }`}>
                    {option.label}
                  </div>
                  {option.description && (
                    <div className={`text-xs sm:text-sm mt-1 transition-colors duration-200 line-clamp-2 ${
                      value === option.value ? 'text-emerald-600' : 'text-slate-500'
                    }`}>
                      {option.description}
                    </div>
                  )}
                </div>
              </div>
              
              {/* Hover effect overlay */}
              <div className={`absolute inset-0 rounded-2xl transition-opacity duration-200 ${
                value === option.value 
                  ? 'bg-emerald-500/5 opacity-100' 
                  : 'bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5'
              }`} />
            </div>
          </label>
        ))}
      </div>
    </div>
  );
};

export default RadioGroup; 